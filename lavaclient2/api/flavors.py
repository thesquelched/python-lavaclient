import logging
from figgis import Config, ListField

from lavaclient2.api import resource
from lavaclient2.api.response import Flavor
from lavaclient2 import constants


LOG = logging.getLogger(constants.LOGGER_NAME)


######################################################################
# API Responses
######################################################################

class FlavorsResponse(Config):

    flavors = ListField(Flavor, required=True)


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
        return self._parse_response(
            self._client._get('/flavors'),
            FlavorsResponse,
            wrapper='flavors')
