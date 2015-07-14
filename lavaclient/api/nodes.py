import logging
import six
from figgis import Config, ListField

from lavaclient.api import resource
from lavaclient import constants
from lavaclient.api.response import Node
from lavaclient.util import command, display, CommandLine

LOG = logging.getLogger(constants.LOGGER_NAME)


######################################################################
# API Responses
######################################################################

class NodesResponse(Config):

    """Response from /clusters/<cluster_id>/nodes"""

    nodes = ListField(Node, required=True)


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Nodes API methods"""
    @command(parser_options=dict(
        description='List all nodes in a cluster'
    ))
    @display(Node.display_nodes)
    def list(self, cluster_id):
        """
        List nodes belonging to the cluster.

        :returns: List of :class:`~lavaclient.api.response.Node` objects
        """
        return self._parse_response(
            self._client._get('clusters/{0}/nodes'.format(cluster_id)),
            NodesResponse,
            wrapper='nodes')
