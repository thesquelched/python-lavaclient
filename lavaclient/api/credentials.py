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

"""
Credential management, e.g. SSH keys, Cloud Files
"""

import six
import logging
from figgis import Config, ListField, Field

from lavaclient.api import resource
from lavaclient.api.response import (Credentials, CloudFilesCredential, SSHKey,
                                     S3Credential, CredentialType)
from lavaclient.validators import Length
from lavaclient.util import (CommandLine, argument, command, display_table,
                             file_or_string)
from lavaclient.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class Credential(Config):

    cloud_files = Field(CloudFilesCredential)
    ssh_keys = Field(SSHKey)
    s3 = Field(S3Credential)


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


class CreateS3Request(Config):

    access_key_id = Field(six.text_type, required=True, nullable=False,
                          validator=Length(min=20, max=20))
    access_secret_key = Field(six.text_type, nullable=False, required=True,
                              validator=Length(min=40, max=40))


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Credentials API methods"""

    def _list(self, type=None):
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

        :returns: List of :class:`Credentials`
                  objects
        """
        return self._list()

    @command(parser_options=dict(
        description='List all SSH keys'
    ))
    @display_table(SSHKey)
    def list_ssh_keys(self):
        """
        List all SSH keys

        :returns: List of :class:`SSHKey` objects
        """
        return self._list(type='ssh_keys')

    @command(parser_options=dict(
        description='List all Cloud Files credentials'
    ))
    @display_table(CloudFilesCredential)
    def list_cloud_files(self):
        """
        List all Cloud Files credentials

        :returns: List of :class:`CloudFilesCredential` objects
        """
        return self._list(type='cloud_files')

    @command(parser_options=dict(
        description='List all Amazon S3 credentials'
    ))
    @display_table(S3Credential)
    def list_s3(self):
        """
        List all Amazon S3 credentials

        :returns: List of :class:`S3Credential` objects
        """
        return self._list(type='s3')

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
            help='SSH public key; must be either a file containing the '
                 'public key or the plaintext public key itself.')
    )
    @display_table(SSHKey)
    def create_ssh_key(self, name, public_key):
        """
        Upload an SSH public key for cluster logins

        :param name: The name to associate to the public key
        :param public_key: SSH public key in plaintext or path to key file
        :returns: :class:`SSHKey`
        """
        data = dict(
            key_name=name,
            public_key=file_or_string(public_key),
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
        Create credentials for Cloud Files access

        :param username: Cloud Files username
        :param api_key: Cloud Files API Key
        :returns: :class:`CloudFilesCredential`
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
            description='Add credentials for Amazon S3'
        ),
        access_key_id=argument(help='Amazon S3 access key id'),
        access_secret_key=argument(help='Amazon S3 access secret key')
    )
    @display_table(S3Credential)
    def create_s3(self, access_key_id, access_secret_key):
        """
        Create credentials for Amazon S3 access

        :param access_key_id: S3 access key id
        :param access_secret_key: S3 access secret key
        :returns: :class:`S3Credential`
        """
        data = dict(
            access_key_id=access_key_id,
            access_secret_key=access_secret_key,
        )
        request_data = self._marshal_request(
            data, CreateS3Request, wrapper='s3')

        resp = self._parse_response(
            self._client._post('credentials/s3', json=request_data),
            CredentialResponse,
            wrapper='credentials')
        return resp.s3

    @command(
        parser_options=dict(
            description='Update SSH key'
        ),
        name=argument(metavar='<name>', help='Name of existing SSH key'),
        public_key=argument(
            help='SSH public key; must be either a file containing the '
                 'public key or the plaintext public key itself.')
    )
    @display_table(SSHKey)
    def update_ssh_key(self, name, public_key):
        """
        Upload an SSH public key for cluster logins

        :param name: The name of an existing SSH key
        :param public_key: SSH public key in plaintext or path to key file
        :returns: :class:`SSHKey`
        """
        data = dict(key_name=name,
                    public_key=file_or_string(public_key))
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
        :returns: :class:`CloudFilesCredential`
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
        parser_options=dict(
            description='Update credentials for Amazon S3'
        ),
        access_key_id=argument(
            help='Access Key Id for existing Amazon S3 credential'),
        access_secret_key=argument(help='Amazon S3 Access Secret Key')
    )
    @display_table(S3Credential)
    def update_s3(self, access_key_id, access_secret_key):
        """
        Update credentials for Amazon S3 access

        :param access_key_id: S3 access key id
        :param access_secret_key: S3 access secret Key
        :returns: :class:`S3Credential`
        """
        data = dict(
            access_key_id=access_key_id,
            access_secret_key=access_secret_key)
        request_data = self._marshal_request(
            data, CreateS3Request, wrapper='s3')

        resp = self._parse_response(
            self._client._put(
                'credentials/s3/{0}'.format(access_key_id),
                json=request_data),
            CredentialResponse,
            wrapper='credentials')
        return resp.s3

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

    @command(
        parser_options=dict(description='Delete Amazon S3 credential'),
        name=argument(help='Amazon S3 access key id')
    )
    def delete_s3(self, access_key_id):
        """
        Delete Amazon s3 credential

        :param access_key_id: S3 access key id
        """
        self._client._delete('credentials/s3/{0}'.format(access_key_id))
