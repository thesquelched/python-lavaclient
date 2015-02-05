import logging
from figgis import Config, ListField, Field

from lavaclient2.api import response, resource
from lavaclient2 import constants


LOG = logging.getLogger(constants.LOGGER_NAME)


######################################################################
# API Responses
######################################################################

class DistroResponse(Config, response.IdReprMixin):

    distro = Field(response.Distro, required=True)


class DistrosResponse(Config):

    distros = ListField(response.Distro, required=True)


######################################################################
# API Resource
######################################################################

class Resource(resource.Resource):

    """Distros API methods"""

    def list(self):
        """
        List all distros

        :returns: list of Distro objects
        """
        return self.parse_response(
            self._client._get('/distros'),
            DistrosResponse,
            wrapper='distros')

    def get(self, distro_id):
        """
        Get a specific distro
        """
        return self.parse_response(
            self._client._get('/distros/{0}'.format(distro_id)),
            DistroResponse,
            wrapper='distro')
