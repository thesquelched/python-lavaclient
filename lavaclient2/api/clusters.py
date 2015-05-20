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

import itertools
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
from lavaclient2.util import (CommandLine, argument, command, display_table,
                              coroutine, create_socks_proxy)
from lavaclient2.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


WAIT_INTERVAL = 30
MIN_INTERVAL = 10


IN_PROGRESS_STATES = frozenset([
    'BUILDING', 'BUILD', 'CONFIGURING', 'CONFIGURED', 'UPDATING', 'REBOOTING',
    'RESIZING', 'WAITING'])
FINAL_STATES = frozenset(['ACTIVE', 'ERROR'])


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

class ClusterCreateScript(Config):

    id = Field(six.text_type, required=True)


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
    scripts = ListField(ClusterCreateScript)


class ClusterResizeRequest(Config):

    """PUT data to resize cluster"""

    node_groups = ListField(ClusterCreateNodeGroups)


class ClusterUpdateRequest(Config):

    """Update a cluster resource"""

    action = Field(six.text_type, required=True,
                   validator=validators.Length(min=1, max=255),
                   choices=['resize'])
    cluster = Field(ClusterResizeRequest)


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
        user_scripts=argument(
            '--user-script', action='append',
            help='User script ID: See `lava2 scripts --help` for more '
                 'information; may be used multiple times to provide multiple '
                 'script IDs'),
        node_groups=argument(
            type=parse_node_group, action='append',
            help='Node group options; may be used multiple times to '
                 'configure multiple node groups. Each option should be in '
                 'the form \'<id>(<key>=<value>, ...)\', where <id> is a '
                 'valid node group ID for the stack and the key-value pairs '
                 'are options to specify for that node group. Current valid '
                 'options are `count` and `flavor_id`'),
        wait=argument(
            action='store_true',
            help='Wait for the cluster to become active'
        ),
    )
    @display_table(ClusterDetail)
    def create(self, name, username, keypair_name, stack_id,
               user_scripts=None, node_groups=None, wait=False):
        """
        Create a cluster

        :param name: Cluster name
        :param username: User to create on the cluster
        :param keypair_name: SSH keypair name
        :param stack_id: Valid stack identifier
        :param node_groups: List of node groups for the cluster
        :param user_scripts: List of user script ID's;
                             See :meth:`Lava.scripts.create`
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

        if user_scripts:
            data.update(scripts=[{'id': script} for script in user_scripts])

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
            description='Resize an existing Lava cluster',
        ),
        node_groups=argument(
            type=parse_node_group, action='append',
            help='Node group options; may be used multiple times to resize '
                 'multiple node groups. Each option should be in the form '
                 '\'<id>(count=<value>)\', where <id> is a valid node '
                 'group ID for the cluster and the count is the '
                 'option to specify new count for that node group. '),
        wait=argument(
            action='store_true',
            help='Wait for the cluster to become active'
        ),
    )
    @display_table(ClusterDetail)
    def resize(self, cluster_id, node_groups=None, wait=False):
        """
        Resize a cluster

        :param cluster_id: ID of cluster to resize
        :param node_groups: List of node groups for the cluster
        :returns: Same as :func:`get`
        """
        if not node_groups:
            raise error.RequestError("Must specify atleast one node_group "
                                     "to resize")

        if not all(sorted(node_group.keys()) == sorted(['count', 'id'])
                   for node_group in node_groups):
            raise error.RequestError("Invalid or missing option "
                                     "in the node groups")

        data = dict(
            action="resize",
            cluster=dict(
                node_groups=node_groups
            )
        )

        request_data = self._marshal_request(data, ClusterUpdateRequest)

        cluster = self._parse_response(
            self._client._put('clusters/{0}'.format(cluster_id),
                              json=request_data),
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

    @coroutine
    def cli_wait_printer(self, start):
        """Coroutine that runs during the wait command. Prints status to stdout if
        the command line is running; otherwise, just log the status."""

        started = False

        while True:
            cluster = yield
            LOG.debug('Cluster {0}: {1}'.format(cluster.id, cluster.status))

            if self._command_line:
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

        start = datetime.now()
        timeout_date = start + delta

        printer = self.cli_wait_printer(start)

        while datetime.now() < timeout_date:
            cluster = self.get(cluster_id)
            printer.send(cluster)

            if cluster.status == 'ACTIVE':
                return cluster
            elif cluster.status not in IN_PROGRESS_STATES:
                raise error.FailedError(
                    'Cluster status is {0}'.format(cluster.status))

            if datetime.now() + timedelta(seconds=interval) >= timeout_date:
                break

            time.sleep(interval)

        raise error.TimeoutError(
            'Cluster did not become active before timeout')

    @command(parser_options=dict(
        description='List all nodes in the cluster'
    ))
    @display_table(Node)
    def nodes(self, cluster_id):
        """
        Get the cluster nodes

        :param cluster_id: Cluster ID
        :returns: nodes of the cluster
        """
        return self._client.nodes.list(cluster_id)

    def _get_named_node(self, nodes, node_name=None):
        if node_name is None:
            return nodes[0]

        try:
            ssh_node = six.next(node for node in nodes
                                if node.name.lower() == node_name.lower())
        except StopIteration:
            raise error.InvalidError(
                'Invalid node: {0}; available nodes are {1}'.format(
                    node_name, ', '.join(node.name for node in nodes)))

        if ssh_node.status.upper() != 'ACTIVE':
            raise error.InvalidError(
                'Node {0} must be ACTIVE, but is {1} instead'.format(
                    node_name, ssh_node.status))

        return ssh_node

    def _cluster_nodes(self, cluster_id, wait=False):
        """
        Return `(cluster, nodes)`, where `nodes` is a list of all nodes in the
        cluster. If the cluster is not ACTIVE/ERROR and wait is `True`, the
        function will block until it becomes active; otherwise, an exception
        is thrown.
        """
        cluster = self.get(cluster_id)
        status = cluster.status.upper()
        if status not in FINAL_STATES:
            LOG.debug('Cluster status: %s', status)

            if status not in IN_PROGRESS_STATES:
                raise error.InvalidError(
                    'Cluster is in state {0}'.format(status))
            elif not wait:
                raise error.InvalidError('Cluster is not yet active')

            self.wait(cluster_id)

        return cluster, self.nodes(cluster_id)

    @command(
        parser_options=dict(
            description='Create a SOCKS5 proxy over SSH to a node in the '
                        'cluster'
        ),
        port=argument(type=int, help='Port on localhost on which to create '
                                     'the proxy'),
        node_name=argument(help='Name of node on which to make the SSH '
                                'connection, e.g. gateway-1. By default, use '
                                'first available node.'),
        ssh_command=argument(help="SSH command (default: 'ssh')"),
        wait=argument(action='store_true',
                      help="Wait for cluster to become active (if it isn't "
                           "already)"),
    )
    def ssh_proxy(self, cluster_id, port=None, node_name=None,
                  ssh_command=None, wait=False):
        """
        Set up a SOCKS5 proxy over SSH to a node in the cluster. Returns the
        SSH process (via :class:`Popen`), which can be stopped via the
        :func:`kill` method.

        :param cluster_id: Cluster ID
        :param port: Local port on which to create the proxy (default: 12345)
        :param node_name: Name of node on which to make the SSH connection. By
                          default, use first available node.
        :param wait: If `True`, wait for the cluster to become active before
                     creating the proxy
        :returns: :class:`Popen` object representing the SSH connection.
        """
        if port is None:
            port = 12345

        cluster, nodes = self._cluster_nodes(cluster_id, wait=wait)
        ssh_node = self._get_named_node(nodes, node_name=node_name)

        # Get a URL to test the proxy against
        all_urls = itertools.chain.from_iterable(
            [component['uri'] for component in node.components
             if 'uri' in component and component['uri'].startswith('http')]
            for node in nodes)
        test_url = six.next(all_urls, None)

        printer = self._cli_printer(LOG)
        printer('Starting SOCKS proxy via node {0} ({1})'.format(
            ssh_node.name, ssh_node.public_ip))

        process = create_socks_proxy(cluster.username, ssh_node.public_ip,
                                     port, ssh_command=ssh_command,
                                     test_url=test_url)

        printer('Successfully created SOCKS proxy on localhost:{0}'.format(
            port), logging.INFO)

        if not self._command_line:
            return process

        try:
            printer('Use Ctrl-C to stop proxy', logging.NOTSET)
            process.communicate()
        except KeyboardInterrupt:
            printer('SOCKS proxy closed')

    @command(
        parser_options=dict(
            description='SSH to a node in the cluster and optionally execute '
                        'a command'
        ),
        node_name=argument(help='Name of node on which to make the SSH '
                                'connection, e.g. gateway-1. By default, use '
                                'first available node.'),
        ssh_command=argument(help="SSH command (default: 'ssh')"),
        wait=argument(action='store_true',
                      help="Wait for cluster to become active (if it isn't "
                           "already)"),
        command=argument(help='Command to execute over SSH')
    )
    def _ssh(self, cluster_id, node_name=None, ssh_command=None, wait=False,
             command=None):
        """
        Command-line only. SSH to the desired cluster node.
        """
        cluster, nodes = self._cluster_nodes(cluster_id, wait=wait)
        node = self._get_named_node(nodes, node_name=node_name)

        output = node._ssh(cluster.username, command=command,
                           ssh_command=ssh_command)
        if command:
            six.print_(output)

    def ssh_execute(self, cluster_id, node_name, command, ssh_command=None,
                    wait=False):
        """
        Execute a command over SSH to the specified node in the cluster.

        :param cluster_id: Cluster ID
        :param node_name: Name of node on which to make the SSH connection. By
                          default, use first available node.
        :param command: Shell command to execute remotely
        :param ssh_command: SSH shell command to execute locally
                            (default: `'ssh'`)
        :param wait: If `True`, wait for the cluster to become active before
                     creating the proxy
        :returns: The output of running the command
        """
        return self._ssh(cluster_id, node_name=node_name,
                         ssh_command=ssh_command, command=command, wait=wait)
