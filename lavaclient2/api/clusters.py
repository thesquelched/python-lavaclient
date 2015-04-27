import argparse
import re
import six
import logging
from figgis import Config, ListField, Field

from lavaclient2.api import resource
from lavaclient2.api.response import Cluster, ClusterDetail
from lavaclient2 import validators
from lavaclient2.util import CommandLine, argument, command, display_table
from lavaclient2.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class ClustersResponse(Config):

    """Response from /clusters"""

    clusters = ListField(Cluster, required=True)


class ClusterResponse(Config):

    """Response from /clusters/<cluster_id>"""

    cluster = Field(ClusterDetail, required=True)


######################################################################
# API Request Data
######################################################################

class ClusterCreateNodeGroups(Config):

    id = Field(six.text_type, required=True,
               validator=validators.Length(min=1, max=255))
    count = Field(int, validator=validators.Range(min=1, max=100))
    flavor_id = Field(six.text_type)


class ClusterCreateRequest(Config):

    """POST data to create cluster"""

    name = Field(six.text_type, required=True,
                 validator=validators.Length(min=1, max=255))
    username = Field(six.text_type, required=True,
                     validator=validators.Length(min=2, max=255))
    keypair_name = Field(six.text_type, required=True,
                         validator=validators.Length(min=1, max=255))
    stack_id = Field(six.text_type, required=True)
    node_groups = ListField(ClusterCreateNodeGroups)


######################################################################
# API Resource
######################################################################

def parse_node_group(value):
    var_rgx = r'(?:[a-zA-Z-]\w*)'
    expr_rgx = r'(?:{var}\s*=\s*.*?)'.format(var=var_rgx)
    node_group_rgx = r'({var})(?:\(({expr}?(?:\s*,\s*{expr})*)\))?$'.format(
        var=var_rgx, expr=expr_rgx)

    match = re.match(node_group_rgx, value)
    if match is None:
        raise argparse.ArgumentTypeError(
            'Invalid node group: {0}'.format(value))

    node_group, argstr = match.groups()

    if argstr:
        exprs = [item.split('=', 1) for item in argstr.split(',')]
        keywords = dict((key.strip(), value.strip()) for key, value in exprs)
    else:
        keywords = {}

    data = {'id': node_group}
    data.update(keywords)

    # Make sure that node group is valid
    ClusterCreateNodeGroups(data)

    return data


@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Clusters API methods"""

    @command
    @display_table(Cluster)
    def list(self):
        """
        List clusters that belong to the tenant specified in the client

        :returns: List of Cluster objects
        """
        return self._parse_response(
            self._client._get('clusters'),
            ClustersResponse,
            wrapper='clusters')

    @command
    @display_table(ClusterDetail)
    def get(self, cluster_id):
        """
        Get the cluster corresponding to the cluster ID

        :param cluster_id: Cluster ID
        :returns: Cluster object
        """
        return self._parse_response(
            self._client._get('clusters/' + six.text_type(cluster_id)),
            ClusterResponse,
            wrapper='cluster')

    @command(node_groups=argument(
        '--node-group', type=parse_node_group, action='append',
        help='Node group options; may be used multiple times to configure '
             'multiple node groups. Each option should be in the form '
             '<id>(<key>=<value>, ...), where <id> is a valid node group ID '
             'for the stack and the key-value pairs are options to specify '
             'for that node group. Current valid options are `count` and '
             '`flavor_id`'))
    @display_table(Cluster)
    def create(self, name, username, keypair_name, stack_id,
               node_groups=None):
        """
        Create a cluster

        :param name: Cluster name
        :param username: User to create on the cluster
        :param keypair_name: SSH keypair name
        :param stack_id: Valid stack identifier
        :param node_groups: List of node groups for the cluster
        :returns: Same as :func:`get`
        """
        data = dict(
            name=name,
            username=username,
            keypair_name=keypair_name,
            stack_id=stack_id
        )
        if node_groups:
            data.update(node_groups=node_groups)

        request_data = self._marshal_request(
            data, ClusterCreateRequest, wrapper='cluster')

        return self._parse_response(
            self._client._post('clusters', json=request_data),
            ClusterResponse,
            wrapper='cluster')

    @command
    def delete(self, cluster_id):
        """
        Delete a cluster

        :param cluster_id: Cluster ID
        :returns: Same as :func:`get`
        """
        self._client._delete('clusters/' + six.text_type(cluster_id))
