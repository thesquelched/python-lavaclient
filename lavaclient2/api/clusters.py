import six
import logging
from figgis import Config, ListField, Field

from lavaclient2.api import response, resource
from lavaclient2 import constants, validators


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


######################################################################
# API Request Data
######################################################################

class ClusterCreateNodeGroups(Config):

    id = Field(six.text_type, required=True,
               validator=validators.Length(min=1, max=255))
    count = Field(int, validator=validators.Range(min=1, max=100))
    flavor_id = Field(six.text_type)


class ClusterCreateRequest(Config):

    """POST data to create clsuter"""

    name = Field(six.text_type, required=True,
                 validator=validators.Length(min=1, max=255))
    keypair_name = Field(six.text_type, required=True,
                         validator=validators.Length(min=1, max=255))
    stack_id = Field(six.text_type, required=True)
    node_groups = ListField(ClusterCreateNodeGroups)


######################################################################
# API Resource
######################################################################

class Resource(resource.Resource):

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
            wrapper='clusters')

    def get(self, cluster_id):
        """
        Get the cluster corresponding to the cluster ID

        :param cluster_id: Cluster ID
        :returns: Cluster object
        """
        return self.parse_response(
            self._client._get('clusters/' + six.text_type(cluster_id)),
            ClusterResponse,
            wrapper='cluster')

    def create(self, name, keypair_name, stack_id, node_groups=None):
        """
        Create a cluster

        :param name: Cluster name
        :param keypair_name: SSH keypair name
        :param stack_id: Valid stack identifier
        :param node_groups: List of node groups for the cluster
        :returns: Same as :func:`get`
        """
        data = dict(
            name=name,
            keypair_name=keypair_name,
            stack_id=stack_id
        )
        if node_groups:
            data.update(node_groups=node_groups)

        request_data = self.marshal_request(
            data, ClusterCreateRequest, wrapper='cluster')

        return self.parse_response(
            self._client._post('clusters', data=request_data),
            ClusterResponse,
            wrapper='cluster')

    def delete(self, cluster_id):
        """
        Delete a cluster

        :param cluster_id: Cluster ID
        :returns: Same as :func:`get`
        """
        return self.parse_response(
            self._client._delete('clusters/' + six.text_type(cluster_id)),
            ClusterResponse,
            wrapper='cluster')
