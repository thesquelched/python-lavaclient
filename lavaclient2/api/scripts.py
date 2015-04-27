import six
import logging
from figgis import Config, ListField, Field

from lavaclient2.api import resource
from lavaclient2.api.response import Script
from lavaclient2.validators import Length
from lavaclient2 import constants


LOG = logging.getLogger(constants.LOGGER_NAME)


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
    type = Field(six.text_type, choices=['POST_INIT'], default='POST_INIT')


######################################################################
# API Resource
######################################################################

class Resource(resource.Resource):

    """Scripts API methods"""

    def list(self):
        """
        List scripts that belong to the tenant specified in the client

        :returns: List of Script objects
        """
        return self._parse_response(
            self._client._get('scripts'),
            ScriptsResponse,
            wrapper='scripts')

    def create(self, name, url, script_type):
        """
        Create a script. Currently only post-init scripts are supported.

        :param name: Script name
        :param url: The URL from which the script may be downloaded
        :param script_type: Script type; currently, must be 'post_init'
        :returns: Same as :func:`get`
        """
        data = dict(
            name=name,
            url=url,
            type=script_type,
        )

        request_data = self._marshal_request(
            data, CreateScriptRequest, wrapper='script')

        return self._parse_response(
            self._client._post('scripts', json=request_data),
            ScriptResponse,
            wrapper='script')

    def update(self, script_id, name=None, url=None, script_type=None):
        """
        Update an existing script.

        :param script_id: ID of existing script
        :param name: Script name
        :param url: The URL from which the script may be downloaded
        :param script_type: Script type; currently, must be 'post_init'
        :returns: Same as :func:`get`
        """
        data = dict(
            name=name,
            url=url,
            type=script_type,
        )

        request_data = self._marshal_request(
            data, CreateScriptRequest, wrapper='script')

        return self._parse_response(
            self._client._put('scripts/{0}'.format(script_id),
                              json=request_data),
            ScriptResponse,
            wrapper='script')

    def delete(self, script_id):
        """
        Delete a script.

        :param script_id: ID of existing script
        """
        self._client._delete('scripts/{0}'.format(script_id))
