#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import re
import six
import logging
import time
import sys
from datetime import datetime, timedelta
from figgis import Config, ListField, Field

from lavaclient2.api import resource
from lavaclient2.api.response import Cluster, ClusterDetail, Node
from lavaclient2 import validators, error
from lavaclient2.util import CommandLine, argument, command, display_table
from lavaclient2.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


WAIT_INTERVAL = 30
MIN_INTERVAL = 10


def natural_number(value):
    intval = int(value)
    if intval < 0:
        raise argparse.ArgumentTypeError('Must be a non-negative integer')

    return intval


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


def elapsed_minutes(start):
    return (datetime.now() - start).total_seconds() / 60


def wait_coroutine(command_line, start):
    """Coroutine that runs during the wait command. Prints status to stdout if
    the command line is running; otherwise, just log the status."""

    started = False

    while True:
        cluster = yield
        LOG.debug('Cluster {0}: {1}'.format(cluster.id, cluster.status))

        if command_line:
            if not started:
                started = True
                cli_msg_length = 0
                six.print_('Waiting for cluster {0}'.format(cluster.id))

            msg = 'Status: {0} (Elapsed time: {1:.1f} minutes)'.format(
                cluster.status, elapsed_minutes(start))
            sys.stdout.write('\b' * cli_msg_length + msg)
            sys.stdout.flush()
            cli_msg_length = len(msg)

            if cluster.status == 'ACTIVE':
                six.print_('\n')


@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Clusters API methods"""

    @command(
        parser_options=dict(
            description='List all existing clusters',
        ),
    )
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

    @command(
        parser_options=dict(
            description='Display an existing cluster in detail',
        ),
    )
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

    @command(
        parser_options=dict(
            description='Create a new Lava cluster',
            epilog='See also: http://www.rackspace.com/knowledge_center/'
                   'article/manage-ssh-key-pairs-for-cloud-servers-with-'
                   'python-novaclient'
        ),
        name=argument(help='Cluster name'),
        username=argument(
            help='Login name of the user to install onto the created nodes'),
        keypair_name=argument(
            help='SSH keypair name, which must have been created beforehand '
                 'in nova.'),
        stack_id=argument(
            help='Valid Lava stack ID. For a list of stacks, use the '
                 '`lava2 stacks list` command'),
        node_groups=argument(
            type=parse_node_group, action='append',
            help='Node group options; may be used multiple times to '
                 'configure multiple node groups. Each option should be in '
                 'the form <id>(<key>=<value>, ...), where <id> is a valid '
                 'node group ID for the stack and the key-value pairs are '
                 'options to specify for that node group. Current valid '
                 'options are `count` and `flavor_id`'),
        wait=argument(
            action='store_true',
            help='Wait for the cluster to become active'
        ),
    )
    @display_table(ClusterDetail)
    def create(self, name, username, keypair_name, stack_id,
               node_groups=None, wait=False):
        """
        Create a cluster

        :param name: Cluster name
        :param username: User to create on the cluster
        :param keypair_name: SSH keypair name
        :param stack_id: Valid stack identifier
        :param node_groups: List of node groups for the cluster
        :param wait: If `True`, wait for the cluster to become active before
                     returning
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

        cluster = self._parse_response(
            self._client._post('clusters', json=request_data),
            ClusterResponse,
            wrapper='cluster')

        if wait:
            return self.wait(cluster.id)

        return cluster

    @command(
        parser_options=dict(
            description='Delete a cluster',
        ),
    )
    def delete(self, cluster_id):
        """
        Delete a cluster

        :param cluster_id: Cluster ID
        :returns: Same as :func:`get`
        """
        self._client._delete('clusters/' + six.text_type(cluster_id))

    @command(
        parser_options=dict(
            description='Poll a cluster until it becomes active'
        ),
        timeout=argument(type=natural_number,
                         help='Poll timeout (in minutes)'),
        interval=argument(type=natural_number,
                          help='Poll interval (in seconds)'),
    )
    @display_table(ClusterDetail)
    def wait(self, cluster_id, timeout=None, interval=None):
        """
        Wait (blocking) for a cluster to either become active or fail.

        :param cluster_id: Cluster ID
        :param timeout: Wait timeout in minutes (default: no timeout)
        :returns: Same as :func:`get`
        """
        if interval is None:
            interval = WAIT_INTERVAL

        interval = max(MIN_INTERVAL, interval)

        delta = timedelta(minutes=timeout) if timeout else timedelta(days=365)
        in_progress_states = frozenset([
            'BUILDING', 'BUILD', 'CONFIGURING', 'CONFIGURED', 'UPDATING',
            'REBOOTING', 'RESIZING', 'WAITING'])

        start = datetime.now()
        timeout_date = start + delta

        printer_coro = wait_coroutine(self._command_line, start)
        printer_coro.send(None)  # Like running next, but py2/3 compatible

        while datetime.now() < timeout_date:
            cluster = self.get(cluster_id)
            printer_coro.send(cluster)

            if cluster.status == 'ACTIVE':
                return cluster
            elif cluster.status not in in_progress_states:
                raise error.FailedError(
                    'Cluster status is {0}'.format(cluster.status))

            if datetime.now() + timedelta(seconds=interval) >= timeout_date:
                break

            time.sleep(interval)

        raise error.TimeoutError(
            'Cluster did not become active before timeout')

    @command
    @display_table(Node)
    def nodes(self, cluster_id):
        """
        Get the cluster nodes
        :param cluster_id:
        :return: nodes of the cluster
        """
        return self._client.nodes.list(cluster_id)
