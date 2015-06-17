#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import six
import logging
from itertools import chain
from figgis import Config, ListField, Field

from lavaclient.api import resource
from lavaclient.api.response import (CloudFilesCredential, SSHKey,
                                     CredentialType)
from lavaclient.validators import Length
from lavaclient.util import (CommandLine, argument, command, display_table,
                             file_or_string, print_table)
from lavaclient.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class Credentials(Config):

    cloud_files = ListField(CloudFilesCredential)
    ssh_keys = ListField(SSHKey)

    def display(self):
        data = chain(
            [('SSH Key', key.name) for key in self.ssh_keys],
            [('Cloud Files', cred.username) for cred in self.cloud_files],
        )
        print_table(data, ('Type', 'Name'))


class Credential(Config):

    cloud_files = Field(CloudFilesCredential)
    ssh_keys = Field(SSHKey)


class CredentialsResponse(Config):

    """Response from /credentials"""

    credentials = Field(Credentials, required=True)


class CredentialResponse(Config):

    credentials = Field(Credential, required=True)


class CredentialTypesResponse(Config):

    credentials = ListField(CredentialType, required=True)


######################################################################
# API Request Data
######################################################################

class CreateSSHKeyRequest(Config):

    key_name = Field(six.text_type, required=True, nullable=False,
                     validator=Length(min=3, max=255))
    public_key = Field(six.text_type, nullable=False, required=True,
                       validator=Length(min=50, max=1024))


class CreateCloudFilesRequest(Config):

    username = Field(six.text_type, required=True, nullable=False,
                     validator=Length(min=3, max=255))
    api_key = Field(six.text_type, nullable=False, required=True,
                    validator=Length(min=20, max=40))


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Credentials API methods"""

    def _list(self, type=None):
        """
        List credentials that belong to the tenant specified in the client

        :param type: Type of credentials to list (defaults to all credentials)
        :returns: List of Credentials objects
        """
        url = 'credentials/' + type if type else 'credentials'
        resp = self._parse_response(
            self._client._get(url),
            CredentialsResponse,
            wrapper='credentials')

        return getattr(resp, type) if type else resp

    @command(parser_options=dict(
        description='List all existing credentials',
    ))
    @display_table(Credentials)
    def list(self):
        """
        List all credentials belonging to the tenant
        """
        return self._list()

    @command(parser_options=dict(
        description='List all SSH keys'
    ))
    @display_table(SSHKey)
    def list_ssh_keys(self):
        """
        List all SSH keys

        :returns: List of SSHKey objects
        """
        return self._list(type='ssh_keys')

    @command(parser_options=dict(
        description='List all Cloud Files credentials'
    ))
    @display_table(CloudFilesCredential)
    def list_cloud_files(self):
        """
        List all Cloud Files credentials

        :returns: List of CloudFilesCredential objects
        """
        return self._list(type='cloud_files')

    def list_types(self):
        """
        List all credential types

        :returns: List of CredentialType objects
        """
        return self._parse_response(
            self._get('credentials/types'),
            CredentialTypesResponse,
            wrapper='credentials')

    @command(
        parser_options=dict(
            description='Upload a SSH public key for cluster logins'
        ),
        name=argument(metavar='<name>',
                      help='Name to associate with the key'),
        public_key=argument(
            type=file_or_string,
            help='SSH public key; must be either a file containing the '
                 'public key or the plaintext public key itself.')
    )
    @display_table(SSHKey)
    def create_ssh_key(self, name, public_key):
        """
        Upload an SSH public key for cluster logins

        :param name: The name to associate to the public key
        :param public_key: SSH public key in plaintext
        """
        data = dict(
            key_name=name,
            public_key=public_key,
        )
        request_data = self._marshal_request(data, CreateSSHKeyRequest,
                                             wrapper='ssh_keys')

        resp = self._parse_response(
            self._client._post('credentials/ssh_keys', json=request_data),
            CredentialResponse,
            wrapper='credentials')
        return resp.ssh_keys

    @command(
        parser_options=dict(
            description='Add credentials for a Cloud Files account'
        ),
        username=argument(help='Cloud Files username'),
        api_key=argument(help='Cloud Files API key')
    )
    @display_table(CloudFilesCredential)
    def create_cloud_files(self, username, api_key):
        """
        Update credentials for Cloud Files access

        :param username: Cloud Files username
        :param api_key: Cloud Files API Key
        """
        data = dict(
            username=username,
            api_key=api_key,
        )
        request_data = self._marshal_request(
            data, CreateCloudFilesRequest, wrapper='cloud_files')

        resp = self._parse_response(
            self._client._post('credentials/cloud_files', json=request_data),
            CredentialResponse,
            wrapper='credentials')
        return resp.cloud_files

    @command(
        parser_options=dict(
            description='Update SSH key'
        ),
        name=argument(metavar='<name>', help='Name of existing SSH key'),
        public_key=argument(
            type=file_or_string,
            help='SSH public key; must be either a file containing the '
                 'public key or the plaintext public key itself.')
    )
    @display_table(SSHKey)
    def update_ssh_key(self, name, public_key):
        """
        Upload an SSH public key for cluster logins

        :param name: The name of an existing SSH key
        :param new_name: The name to associate to the public key
        :param public_key: SSH public key in plaintext
        """
        data = dict(key_name=name,
                    public_key=public_key)
        request_data = self._marshal_request(data, CreateSSHKeyRequest,
                                             wrapper='ssh_keys')

        resp = self._parse_response(
            self._client._put('credentials/ssh_keys/{0}'.format(name),
                              json=request_data),
            CredentialResponse,
            wrapper='credentials')
        return resp.ssh_keys

    @command(
        parser_options=dict(
            description='Add credentials for a Cloud Files account'
        ),
        username=argument(
            help='Username for existing Cloud Files credential'),
        api_key=argument(help='Cloud Files API key')
    )
    @display_table(CloudFilesCredential)
    def update_cloud_files(self, username, api_key):
        """
        Update credentials for Cloud Files access

        :param username: Cloud Files username
        :param api_key: Cloud Files API Key
        """
        data = dict(
            username=username,
            api_key=api_key)
        request_data = self._marshal_request(
            data, CreateCloudFilesRequest, wrapper='cloud_files')

        resp = self._parse_response(
            self._client._put(
                'credentials/cloud_files/{0}'.format(username),
                json=request_data),
            CredentialResponse,
            wrapper='credentials')
        return resp.cloud_files

    @command(
        parser_options=dict(description='Delete an SSH key'),
        name=argument(help='SSH key name')
    )
    def delete_ssh_key(self, name):
        """
        Delete SSH key

        :param name: Name that identifies the SSH key
        """
        self._client._delete('credentials/ssh_keys/{0}'.format(name))

    @command(
        parser_options=dict(description='Delete a Cloud Files credential'),
        name=argument(help='Cloud Files username')
    )
    def delete_cloud_files(self, username):
        """
        Delete Cloud Files credential

        :param username: Cloud Files username
        """
        self._client._delete('credentials/cloud_files/{0}'.format(username))
