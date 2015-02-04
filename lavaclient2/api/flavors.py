import logging
from figgis import Config, ListField, Field

from lavaclient2.api import response, resource
from lavaclient2 import constants


LOG = logging.getLogger(constants.LOGGER_NAME)


######################################################################
# API Responses
######################################################################

class FlavorResponse(Config, response.IdReprMixin):

    flavor = Field(response.Flavor, required=True)


class FlavorsResponse(Config):

    flavors = ListField(response.Flavor, required=True)


######################################################################
# API Resource
######################################################################

class Resource(resource.Resource):

    """Flavors API methods"""

    def list(self):
        """
        List all flavors

        :returns: list of Flavor objects
        """
        return self.parse_response(
            self._client._get('/flavors'),
            FlavorsResponse,
            wrapper='flavors')

    def get(self, flavor_id):
        """
        Get a specific flavor
        """
        return self.parse_response(
            self._client._get('/flavors/{0}'.format(flavor_id)),
            FlavorResponse,
            wrapper='flavor')
