import six
import logging
from figgis import Config, ListField, Field

from lavaclient2.api import response, method
from lavaclient2 import constants


LOG = logging.getLogger(constants.LOGGER_NAME)


######################################################################
# API Responses
######################################################################

class ClustersResponse(Config):

    """Response from /clusters"""

    clusters = ListField(response.Cluster, required=True)


class ClusterResponse(Config):

    """Response from /clusters/<cluster_id>"""

    cluster = Field(response.Cluster, required=True)


class ClustersApi(method.ApiMethod):

    """Clusters API methods"""

    def __init__(self, client):
        self._client = client

    def list(self):
        """
        List clusters that belong to the tenant specified in the client

        :returns: List of Cluster objects
        """
        return self.parse_response(
            self._client._get('clusters'),
            ClustersResponse,
            wrapper='clusters'
        )

    def get(self, cluster_id):
        """
        Get the cluster corresponding to the cluster ID

        :param cluster_id: Lava Cluster ID
        :returns: Cluster object
        """
        return self.parse_response(
            self._client._get('clusters/' + six.text_type(cluster_id)),
            ClusterResponse,
            wrapper='cluster'
        )
