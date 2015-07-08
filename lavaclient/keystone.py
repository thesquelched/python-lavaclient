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
keystoneclient extension for API Key Authentication
"""

import logging
import six

from keystoneclient.i18n import _
from keystoneclient.v2_0 import client as v2_client
from keystoneclient.auth.identity import v2 as v2_auth
from keystoneclient.exceptions import (
    AuthorizationFailure, Unauthorized, EndpointNotFound)

from lavaclient.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


class ApiKeyAuth(v2_auth.Auth):

    """Keystone v2 API Key Authenticator"""

    def __init__(self, auth_url, api_key, username=None, tenant_id=None):
        super(ApiKeyAuth, self).__init__(auth_url, tenant_id=tenant_id)
        self.api_key = api_key
        self.username = username

    def get_auth_data(self, headers=None):
        return {
            "RAX-KSKEY:apiKeyCredentials": {
                "username": self.username,
                "apiKey": self.api_key,
            },
        }


class PasswordAuth(v2_auth.Password):
    def get_auth_data(self, *args, **kwargs):
        data = super(PasswordAuth, self).get_auth_data(*args, **kwargs)
        data.update({
            "RAX-AUTH:domain": {
                "name": "Rackspace"
            }
        })

        return data


class Client(v2_client.Client):

    def __init__(self, api_key=None, **kwargs):
        """Initialize a new client for the Keystone v2.0 API using an API
        key or password."""

        if not any((api_key, kwargs.get('password'))):
            raise ValueError(_(
                "Cannot authenticate without an api_key or password"))

        if kwargs.get('username') is None:
            raise ValueError(_("Cannot authenticate without a username"))

        self._api_key = api_key

        super(Client, self).__init__(**kwargs)

    def get_auth_plugin(self, auth_url, api_key, username, password,
                        project_id, tenant_id):
        if api_key is not None:
            return ApiKeyAuth(auth_url,
                              api_key,
                              username=username or self.username,
                              tenant_id=project_id or tenant_id)
        if password is not None:
            return PasswordAuth(auth_url,
                                username=username or self.username,
                                password=password,
                                tenant_id=project_id or tenant_id)

        raise ValueError(_(
            "Cannot authenticate without an api_key or password"))

    def get_raw_token_from_identity_service(self, auth_url, username=None,
                                            api_key=None, tenant_id=None,
                                            password=None, project_id=None,
                                            **kwargs):
        """Authenticate against the v2 Identity API using an API key.

        :returns: access.AccessInfo if authentication was successful.
        :raises keystoneclient.AuthorizationFailure: if unable to authenticate
            or validate the existing authorization token
        """
        if api_key is None:
            api_key = self._api_key

        if password is None:
            password = self.password

        try:
            if auth_url is None:
                raise ValueError(_("Cannot authenticate without an auth_url"))

            plugin = self.get_auth_plugin(auth_url, api_key, username,
                                          password, project_id, tenant_id)

            return plugin.get_auth_ref(self.session)
        except (AuthorizationFailure, Unauthorized) as exc:
            LOG.debug("Authorization Failed.", exc_info=exc)
            raise
        except EndpointNotFound as exc:
            msg = _(
                'There was no suitable authentication url for this request')
            six.raise_from(AuthorizationFailure(msg), exc)
        except Exception as exc:
            msg = _("Authorization Failed: {0}".format(exc))
            six.raise_from(AuthorizationFailure(msg), exc)
