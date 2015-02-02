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

import logging
import six
import re
from keystoneclient import exceptions as ks_error

from lavaclient2 import keystone
from lavaclient2 import util
from lavaclient2 import constants
from lavaclient2 import error


LOG = logging.getLogger(constants.LOGGER_NAME)


class Lava(object):

    """Lava API Client"""

    def __init__(self,
                 api_key,
                 username,
                 region,
                 auth_url=None,
                 tenant_id=None,
                 endpoint=None):
        """
        Lava(api_key, username, region, [auth_url, tenant_id, endpoint])

        Create a Lava API client using your API key and username.
        Authentication is handled via Keystone.

        :param api_key: API key string
        :param username: Username string
        :param region: Region identifier, e.g. 'DFW'
        :param auth_url: Override Keystone authentication url (optional)
        :param tenant_id: Your Rackspace tenant ID (optional)
        :param endpoint: Override Cloud Big Data endpoint URL (optional)
        """
        if api_key is None:
            raise error.InvalidError("Missing api_key")

        if username is None:
            raise error.InvalidError("Missing username")

        if region is None:
            raise error.InvalidError('Missing region')

        # Ensure tenant_id is unicode
        if tenant_id is not None:
            tenant_id = six.text_type(tenant_id)

        if auth_url is None:
            auth_url = constants.DEFAULT_AUTH_URL

        self._auth = self.authenticate(auth_url,
                                       api_key,
                                       region,
                                       username,
                                       tenant_id)

        if endpoint is None:
            self._endpoint = self._get_endpoint(region, tenant_id)
        else:
            self._endpoint = self._validate_endpoint(endpoint, tenant_id)

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
            region_name=region)

        if tenant_id:
            filters.update(attr='tenantId', filter_value=tenant_id)

        try:
            return self._auth.service_catalog.url_for(**filters)
        except ks_error.EndpointNotFound as exc:
            LOG.critical('Error getting endpoint: {0}'.format(exc),
                         exc_info=exc)
            raise error.InvalidError(str(exc))

    def authenticate(self, auth_url, api_key, region, username, tenant_id):
        """Return keystone authentication client"""
        try:
            return keystone.ApiKeyClient(
                auth_url=util.strip_url(auth_url),
                api_key=api_key,
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

    @property
    def token(self):
        return self._auth.auth_token

    @property
    def endpoint(self):
        return self._endpoint
