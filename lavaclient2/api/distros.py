import six
import logging
from figgis import Config, ListField, Field

from lavaclient2.api import resource
from lavaclient2.api.response import Distro, DistroDetail
from lavaclient2.util import CommandLine, command, display_table
from lavaclient2.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class DistroResponse(Config):

    distro = Field(DistroDetail, required=True)


class DistrosResponse(Config):

    distros = ListField(Distro, required=True)


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Distros API methods"""

    @command
    @display_table(Distro)
    def list(self):
        """
        List all distros

        :returns: list of Distro objects
        """
        return self._parse_response(
            self._client._get('/distros'),
            DistrosResponse,
            wrapper='distros')

    @command
    @display_table(DistroDetail)
    def get(self, distro_id):
        """
        Get a specific distro
        """
        return self._parse_response(
            self._client._get('/distros/{0}'.format(distro_id)),
            DistroResponse,
            wrapper='distro')
