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
from figgis import Config, ListField, Field

from lavaclient.api import resource
from lavaclient.api.response import Script
from lavaclient.validators import Length
from lavaclient.util import (display_table, CommandLine, command, argument,
                             confirm)
from lavaclient.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class ScriptsResponse(Config):

    """Response from /scripts"""

    scripts = ListField(Script, required=True)


class ScriptResponse(Config):

    """Response from /scripts/<script_id>"""

    script = Field(Script, required=True)


######################################################################
# API Request Data
######################################################################

class CreateScriptRequest(Config):

    name = Field(six.text_type, required=True,
                 validator=Length(min=1, max=255))
    url = Field(six.text_type, required=True)
    type = Field(six.text_type, choices=['POST_INIT'])


class UpdateScriptRequest(Config):

    name = Field(six.text_type, validator=Length(min=1, max=255))
    url = Field(six.text_type)
    type = Field(six.text_type, choices=['POST_INIT', None])


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Scripts API methods"""

    @command(parser_options=dict(
        description='List all existing cluster scripts',
    ))
    @display_table(Script)
    def list(self):
        """
        List scripts that belong to the tenant specified in the client

        :returns: List of :class:`~lavaclient.api.response.Script` objects
        """
        return self._parse_response(
            self._client._get('scripts'),
            ScriptsResponse,
            wrapper='scripts')

    @command(
        parser_options=dict(
            description='Create a cluster script',
        ),
        name=argument(help='Descriptive name for this script'),
        url=argument(help='The URL from which the script may be downloaded'),
        script_type=argument(metavar='<type>',
                             choices=['post_init'],
                             help='The type of script, e.g post-init script')
    )
    @display_table(Script)
    def create(self, name, url, script_type):
        """
        Create a script. Currently only post-init scripts are supported.

        :param name: Script name
        :param url: The URL from which the script may be downloaded
        :param script_type: Script type; currently, must be 'post_init'
        :returns: :class:`~lavaclient.api.response.Script`
        """
        data = dict(
            name=name,
            url=url,
            type=script_type.upper(),
        )

        request_data = self._marshal_request(
            data, CreateScriptRequest, wrapper='script')

        return self._parse_response(
            self._client._post('scripts', json=request_data),
            ScriptResponse,
            wrapper='script')

    @command(
        parser_options=dict(
            description='Update an existing script',
        ),
        name=argument(help='Descriptive name for this script'),
        url=argument(help='The URL from which the script may be downloaded'),
        script_type=argument('--type',
                             choices=['post_init'],
                             help='The type of script, e.g post-init script')
    )
    @display_table(Script)
    def update(self, script_id, name=None, url=None, script_type=None):
        """
        Update an existing script.

        :param script_id: ID of existing script
        :param name: Script name
        :param url: The URL from which the script may be downloaded
        :param script_type: Script type; currently, must be 'post_init'
        :returns: :class:`~lavaclient.api.response.Script`
        """
        params = [('name', name),
                  ('url', url),
                  ('type', script_type.upper() if script_type else None)]
        data = {}
        for key, value in params:
            if value is not None:
                data[key] = value

        request_data = self._marshal_request(
            data, UpdateScriptRequest, wrapper='script')

        return self._parse_response(
            self._client._put('scripts/{0}'.format(script_id),
                              json=request_data),
            ScriptResponse,
            wrapper='script')

    @command(
        parser_options=dict(description='Delete a cluster script'),
        do_confirm=argument('--force', action='store_false',
                            help='Suppress delete confirmation dialog'),
    )
    def _delete(self, script_id, do_confirm=True):
        if do_confirm and not confirm('Delete script {0}?'.format(script_id)):
            return

        return self.delete(script_id)

    def delete(self, script_id):
        """
        Delete a script.

        :param script_id: ID of existing script
        """
        self._client._delete('scripts/{0}'.format(script_id))
