import six
import logging
from figgis import Config, ListField

from lavaclient2.api import resource
from lavaclient2.api.response import Flavor
from lavaclient2.util import CommandLine, command, display_table
from lavaclient2.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class FlavorsResponse(Config):

    flavors = ListField(Flavor, required=True)


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Flavors API methods"""

    @command
    @display_table(Flavor)
    def list(self):
        """
        List all flavors

        :returns: list of Flavor objects
        """
        return self._parse_response(
            self._client._get('/flavors'),
            FlavorsResponse,
            wrapper='flavors')
