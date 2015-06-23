# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Lava client setup and authentication
"""

import logging
import six
import re
from keystoneclient import exceptions as ks_error
import uuid
import requests
from threading import Lock

from lavaclient._version import __version__
from lavaclient import keystone
from lavaclient import util
from lavaclient import constants
from lavaclient import error
from lavaclient.log import NullHandler
from lavaclient.api import (clusters, limits, flavors, stacks, distros,
                            workloads, scripts, nodes, credentials)


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


class Lava(object):
    """
    Lava(username, region=None, password=None, token=None, api_key=None, \
auth_url=None, tenant_id=None, endpoint=None, verify_ssl=None)

    CloudBigData API client. Creating an instance will automatically attempt to
    authenticate.

    :param username: Rackspace username
    :param region: Region identifier, e.g. 'DFW'
    :param api_key: API key string
    :param token: API token from previous authentication
    :param password: Keystone auth password
    :param auth_url: Override Keystone authentication url; typically left at
                     the default
    :param tenant_id: Rackspace tenant ID
    :param endpoint: CloudBigData endpoint URL; usually discovered
                     automatically with a valid `region`
    """

    def __init__(self,
                 username,
                 region=None,
                 password=None,
                 token=None,
                 api_key=None,
                 auth_url=None,
                 tenant_id=None,
                 endpoint=None,
                 verify_ssl=None,
                 _enable_cli=False):
        if not any((api_key, password, token)):
            raise error.InvalidError("One of api_key, token, or password is "
                                     "required")

        if not endpoint and not region:
            raise error.InvalidError('One of endpoint or region is required')

        # Ensure tenant_id is unicode
        if tenant_id is not None:
            tenant_id = six.text_type(tenant_id)

        if auth_url is None:
            auth_url = constants.DEFAULT_AUTH_URL

        self._auth_url = auth_url
        self._region = region
        self._api_key = api_key
        self._password = password
        self._username = username
        self._tenant_id = tenant_id
        self._verify_ssl = verify_ssl
        self._token = token

        if token and not endpoint:
            raise error.InvalidError(
                'Token must be accompanied by a hard-coded endpoint')
        elif token:
            self._auth = None
        else:
            if username is None:
                raise error.InvalidError("Missing username")

            self._auth = self._authenticate(auth_url,
                                            api_key,
                                            region,
                                            username,
                                            password,
                                            tenant_id)

        if endpoint is None:
            self._endpoint = self._get_endpoint(region, tenant_id)
        else:
            self._endpoint = self._validate_endpoint(endpoint, tenant_id)

        # Initialize API resources
        self.clusters = clusters.Resource(self, command_line=_enable_cli)
        self.limits = limits.Resource(self, command_line=_enable_cli)
        self.flavors = flavors.Resource(self, command_line=_enable_cli)
        self.stacks = stacks.Resource(self, command_line=_enable_cli)
        self.distros = distros.Resource(self, command_line=_enable_cli)
        self.workloads = workloads.Resource(self, command_line=_enable_cli)
        self.scripts = scripts.Resource(self, command_line=_enable_cli)
        self.nodes = nodes.Resource(self, command_line=_enable_cli)
        self.credentials = credentials.Resource(self,
                                                command_line=_enable_cli)

        self._auth_lock = Lock()

    def _validate_endpoint(self, endpoint, tenant_id):
        """Validate that the endpoint ends with v2/<tenant_id>"""

        endpoint = endpoint.rstrip('/')

        if tenant_id is None:
            if re.search(r'v2/[^/]+$', endpoint):
                return endpoint

            raise error.InvalidError('Endpoint must end with v2/<tenant_id>')

        if endpoint.endswith('v2/{0}'.format(tenant_id)):
            return endpoint
        elif endpoint.endswith('v2'):
            return '{0}/{1}'.format(endpoint, tenant_id)

        raise error.InvalidError('Endpoint must end with v2 or v2/<tenant_id>')

    def _get_endpoint(self, region, tenant_id):
        filters = dict(
            service_type=constants.CBD_SERVICE_TYPE,
            region_name=region.upper())

        if tenant_id:
            filters.update(attr='tenantId', filter_value=tenant_id)

        try:
            return self._auth.service_catalog.url_for(**filters)
        except ks_error.EndpointNotFound as exc:
            LOG.critical('Error getting endpoint: {0}'.format(exc),
                         exc_info=exc)
            raise error.InvalidError(str(exc))

    def _authenticate(self, auth_url, api_key, region, username, password,
                      tenant_id):
        """Return keystone authentication client"""
        try:
            return keystone.Client(
                auth_url=util.strip_url(auth_url),
                api_key=api_key,
                password=password,
                region=region,
                username=username,
                tenant_id=tenant_id)
        except ks_error.AuthorizationFailure as exc:
            LOG.critical('Unable to authenticate', exc_info=exc)
            raise error.AuthenticationError(
                'Authentication error: {0}'.format(exc))
        except ks_error.Unauthorized as exc:
            LOG.critical('Authorization error', exc_info=exc)
            raise error.AuthorizationError(
                'Authorization error: {0}'.format(exc))

    def reauthenticate(self):
        """Reauthenticate with keystone, assuming our token is no longer
        valid"""
        if self._token:
            raise error.AuthenticationError(
                'Can not reauthenticate with hard-coded token')

        with self._auth_lock:
            LOG.info('Reauthenticating via keystone')

            old_token = self.token
            self._auth = self._authenticate(self._auth_url,
                                            self._api_key,
                                            self._region,
                                            self._username,
                                            self._password,
                                            self._tenant_id)

            if self.token == old_token:
                LOG.warn('Reauthentication produced the same token')

    @property
    def token(self):
        """Authentication token; may be passed as `token` option to
        :class:`Lava`"""
        return self._token or self._auth.auth_token

    @property
    def endpoint(self):
        """CloudBigData endpoint; may be passed as `endpoint` option to
        :class:`Lava`"""
        return self._endpoint.rstrip('/')

    ######################################################################
    # Request methods
    ######################################################################

    def _get(self, path, **kwargs):
        """Make a GET request, same as requests.get"""
        return self._request('GET', path, **kwargs)

    def _post(self, path, **kwargs):
        """Make a POST request, same as requests.post"""
        return self._request('POST', path, **kwargs)

    def _put(self, path, **kwargs):
        """Make a PUT request, same as requests.put"""
        return self._request('PUT', path, **kwargs)

    def _delete(self, path, **kwargs):
        """Make a DELETE request, same as requests.delete"""
        return self._request('DELETE', path, **kwargs)

    def _generate_headers(self):
        """Generate request headers"""
        return {
            'X-Auth-Token': self.token,
            'Client-Request-ID': six.text_type(uuid.uuid4()),
            'User-Agent': 'python-lavaclient {0}'.format(__version__),
        }

    def _request(self, method, path, reauthenticate=True, **kwargs):
        """Same as requests.request, but automatically injects
        authentication headers into request and prepends endpoint to path"""
        if self._verify_ssl is not None:
            kwargs['verify'] = kwargs.get('verify', self._verify_ssl)

        headers = kwargs.get('headers') or {}
        headers.update(self._generate_headers())
        kwargs['headers'] = headers

        url = '{0}/{1}'.format(self.endpoint, path.lstrip('/'))

        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code != requests.codes.unauthorized:
                try:
                    msg = exc.response.json()['fault']['message']
                except (KeyError, ValueError):
                    msg = exc.response.text or str(exc)

                six.raise_from(
                    error.RequestError(msg, code=exc.response.status_code),
                    exc)

            if reauthenticate:
                self.reauthenticate()
                return self._request(method, path, reauthenticate=False,
                                     **kwargs)

            msg = '{0} /{1}: Unauthorized'.format(
                method.upper(), path.lstrip('/'))
            LOG.critical(msg, exc_info=exc)
            six.raise_from(error.AuthorizationError(msg), exc)
        except requests.exceptions.RequestException as exc:
            msg = '{0} /{1}: Error encountered during request'.format(
                method.upper(), path.lstrip('/'))
            LOG.critical(msg, exc_info=exc)
            six.raise_from(error.RequestError(msg), exc)

        try:
            return resp.json()
        except ValueError:
            return resp
