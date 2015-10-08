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

import logging
import subprocess
import textwrap
import six
from itertools import chain, repeat
from figgis import Config, Field, ListField
from dateutil.parser import parse as dateparse
from datetime import datetime

from lavaclient.validators import Length, Range
from lavaclient.util import (display_result, prettify, ssh_to_host,
                             print_table, no_nulls)
from lavaclient.log import NullHandler
from lavaclient import error


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


def DateTime(value):
    """Parse a datetime object from a string value"""
    if isinstance(value, datetime):
        return value

    return dateparse(value)


class ReprMixin(object):
    """Defines a standard __repr__ method for response objects"""

    def __repr__(self):
        properties = set(
            key for key, value in six.iteritems(self.__class__.__dict__)
            if not key.startswith('_') and isinstance(value, property))

        # 'id' and 'name' always go at the front of the list
        ordered = []
        for key in ('id', 'name'):
            if key in properties:
                ordered.append("{0}='{1}'".format(key, getattr(self, key)))
                properties.remove(key)

        # Next come any other id's
        ids = []
        for key in list(properties):
            if key.endswith('_id'):
                ids.append(key)
                properties.remove(key)

        ordered.extend(sorted(ids))
        ordered.extend(sorted(properties))

        return '{0}({1})'.format(self.__class__.__name__, ', '.join(ordered))


######################################################################
# Reponse objects
######################################################################

class Link(Config, ReprMixin):

    rel = Field(six.text_type, required=True)
    href = Field(six.text_type, required=True)


class Address(Config, ReprMixin):

    address = Field(six.text_type, required=True, key='addr')
    version = Field(six.text_type, required=True)


class Addresses(Config, ReprMixin):

    public = ListField(Address, required=True,
                       help='See: :class:`Address`')
    private = ListField(Address, required=True,
                        help='See: :class:`Address`')


@prettify('components')
class Node(Config, ReprMixin):
    table_columns = ('id', 'name', 'node_group', 'status',
                     'public_ip', 'private_ip')
    table_header = ('ID', 'Name', 'Role', 'Status', 'Public IP',
                    'Private IP')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    created = Field(DateTime, required=True,
                    help=':py:class:`~datetime.datetime` corresponding to '
                         'creation date')
    updated = Field(DateTime, required=True,
                    help=':py:class:`~datetime.datetime` corresponding to '
                         'date last updated')
    status = Field(six.text_type, required=True)
    flavor_id = Field(six.text_type, required=True)
    addresses = Field(Addresses, required=True,
                      help='Public and private IP addresses; See: '
                           ':class:`Addresses`')
    node_group = Field(six.text_type, required=True, help='Node group ID')
    components = ListField(dict, required=True,
                           help='Components installed on this node, e.g. '
                                '`HiveClient`')

    @classmethod
    def display_nodes(cls, nodes):
        display_result(nodes, Node, title='Nodes')

        six.print_()
        rows = []
        for node in nodes:
            node_column = chain([node.name], repeat(''))

            rows.extend(
                no_nulls([name, comp['name'], comp['nice_name'],
                          comp.get('uri')])
                for name, comp in six.moves.zip(node_column, node.components))

        print_table(rows, ('Node', 'ID', 'Name', 'URI'), title='Components')

    @property
    def private_ip(self):
        """Private IP address on service network"""
        try:
            return self.addresses.private[0].address
        except IndexError:
            return None

    @property
    def public_ip(self):
        """Public IP address"""
        try:
            return self.addresses.public[0].address
        except IndexError:
            return None

    def _ssh(self, username, command=None, ssh_command=None):
        """
        SSH to this node, optionally running a command and returning the
        output.

        :param username: Login user
        :param command: Command to execute remotely
        :param ssh_command: ssh command string or `list`, e.g.
                            `ssh -F configfile`
        :returns: Output from running command, if a command was specified
        """
        try:
            return ssh_to_host(username, self.public_ip, command=command,
                               ssh_command=ssh_command)
        except subprocess.CalledProcessError as exc:
            msg = 'Command failed with code %d', exc.returncode
            LOG.error(msg)
            LOG.debug('Command output:\n%s', exc.output)
            raise error.FailedError(msg)

    def execute(self, username, command, ssh_command=None):
        """
        Execute a command remotely on this node, returning the output.

        :param username: Login user
        :param command: Command to execute remotely
        :param ssh_command: ssh command string or `list`, e.g.
                            `ssh -F configfile`
        :returns: Output from running command
        """
        return self._ssh(username, command=command, ssh_command=ssh_command)


@prettify('components')
class NodeGroup(Config, ReprMixin):
    """Group of nodes that share the same flavor and installed services"""

    table_columns = ('id', 'flavor_id', 'count', '_components')
    table_header = ('ID', 'Flavor', 'Count', 'Components')

    id = Field(six.text_type, required=True,
               validator=Length(min=1, max=255))
    count = Field(int, validator=Range(min=1, max=100))
    flavor_id = Field(six.text_type)
    components = ListField(dict, default={})


class ClusterScript(Config, ReprMixin):

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    status = Field(six.text_type, required=True)


class BaseCluster(object):

    @property
    def nodes(self):
        """See: :meth:`~lavaclient.api.clusters.Resource.nodes`"""
        return self._client.clusters.nodes(self.id)

    def refresh(self):
        """
        Refresh the cluster. If this object was returned from
        :meth:`~lavaclient.api.clusters.Resource.list`, it will return the
        same amount of detail as
        :meth:`~lavaclient.api.clusters.Resource.get`.

        :returns: :class:`ClusterDetail`
        """
        return self._client.clusters.get(self.id)

    def delete(self):
        """
        Delete this cluster.
        """
        return self._client.clusters.delete(self.id)

    def wait(self, **kwargs):
        """
        wait(timeout=None, interval=None)

        Wait for this cluster to become active. See:
        :meth:`~lavaclient.api.clusters.Resource.wait`

        :returns: :class:`ClusterDetail`
        """
        return self._client.clusters.wait(self.id, **kwargs)

    def ssh_proxy(self, **kwargs):
        """
        ssh_proxy(port=None, node_name=None, ssh_command=None, wait=False)

        Start a SOCKS5 proxy over SSH to this cluster. See
        :meth:`~lavaclient.api.clusters.Resource.ssh_proxy`.
        """
        return self._client.clusters.ssh_proxy(self.id, **kwargs)

    def execute_on_node(self, node_name, command, **kwargs):
        """
        execute_on_node(node_name, command, ssh_command=None, wait=False)

        Execute a command on a cluster node. See:
        :meth:`~lavaclient.api.clusters.Resource.ssh_execute`.
        """
        return self._client.clusters.ssh_execute(self.id, node_name, command,
                                                 **kwargs)


class Cluster(Config, ReprMixin, BaseCluster):

    """Basic cluster information"""

    table_columns = ('id', 'name', 'status', 'stack_id', 'created')
    table_header = ('ID', 'Name', 'Status', 'Stack', 'Created')

    id = Field(six.text_type, required=True)
    created = Field(DateTime, required=True,
                    help=':py:class:`~datetime.datetime` corresponding to '
                         'creation date')
    updated = Field(DateTime, required=True,
                    help=':py:class:`~datetime.datetime` corresponding to '
                         'date last updated')
    name = Field(six.text_type, required=True)
    status = Field(six.text_type, required=True)
    stack_id = Field(six.text_type, required=True)
    cbd_version = Field(int, required=True,
                        help='API version at which cluster was created')
    links = ListField(Link)


class ClusterDetail(Config, ReprMixin, BaseCluster):
    """Detailed cluster information"""

    def parse_cluster_credentials(value):
        result = {
            's3': [],
            'cloud_files': [],
            'ambari': [],
            'ssh_keys': [],
        }

        attr_names = {
            's3': 'access_key_id',
            'cloud_files': 'username',
            'ambari': 'username',
            'ssh_keys': 'key_name',
        }

        for item in value:
            type_ = item['type']
            cred = {'type': type_, attr_names[type_]: item['name']}
            result[type_].append(cred)

        return Credentials(result)

    __inherits__ = [Cluster]

    table_columns = ('id', 'name', 'status', 'stack_id', 'created',
                     'cbd_version', 'username', 'progress')
    table_header = ('ID', 'Name', 'Status', 'Stack', 'Created', 'CBD Version',
                    'Username', 'Progress')

    node_groups = ListField(NodeGroup, required=True,
                            help='See: :class:`NodeGroup`')
    username = Field(six.text_type, required=True)
    scripts = ListField(ClusterScript, required=True,
                        help='See: :class:`ClusterScript`')
    progress = Field(float, required=True)
    credentials = Field(parse_cluster_credentials, required=True)

    def display(self):
        display_result(self, ClusterDetail, title='Cluster')

        if self.node_groups:
            six.print_()
            display_result(self.node_groups, NodeGroup, title='Node Groups')

        if self.scripts:
            six.print_()
            display_result(self.scripts, ClusterScript, title='Scripts')


class Flavor(Config, ReprMixin):

    table_columns = ('id', 'name', 'ram', 'vcpus', 'disk')
    table_header = ('ID', 'Name', 'RAM', 'VCPUs', 'Disk')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    disk = Field(int, required=True, help='Disk space in MB')
    vcpus = Field(int, required=True)
    ram = Field(int, required=True, help='Memory in MB')
    links = ListField(Link)


class ServiceComponent(Config, ReprMixin):

    name = Field(six.text_type, required=True)
    mode = Field(six.text_type)


class DistroServiceMode(Config, ReprMixin):

    name = Field(six.text_type, required=True)


@prettify('components')
class DistroService(Config, ReprMixin):

    table_columns = ('name', 'version', '_components', '_description')
    table_header = ('Name', 'Version', 'Components', 'Description')

    name = Field(six.text_type, required=True)
    version = Field(six.text_type, required=True)
    description = Field(six.text_type, required=True)
    components = ListField(dict, required=True)

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 30))


class ResourceLimits(Config, ReprMixin):

    max_count = Field(int, required=True)
    min_count = Field(int, required=True)
    min_ram = Field(int, required=True)


@prettify('components', 'resource_limits')
class StackNodeGroup(Config, ReprMixin):

    table_columns = ('id', 'flavor_id', 'count', 'resource_limits.min_ram',
                     'resource_limits.min_count',
                     'resource_limits.max_count')
    table_header = ('ID', 'Flavor', 'Count', 'Min RAM', 'Min count',
                    'Max Count')

    id = Field(six.text_type, required=True)
    flavor_id = Field(six.text_type, required=True)
    resource_limits = Field(ResourceLimits, required=True,
                            help='See: :class:`ResourceLimits`')
    count = Field(int, required=True)
    components = ListField(dict, required=True)


class StackService(Config, ReprMixin):

    name = Field(six.text_type, required=True)
    modes = ListField(six.text_type, required=True)


class BaseStack(object):

    def refresh(self):
        """
        Refresh this stack. If this object was returned from
        :meth:`~lavaclient.api.stacks.Resource.list`, it will be converted
        into :class:`StackDetail`

        :returns: :class:`StackDetail`
        """
        return self._client.stacks.get(self.id)

    def delete(self):
        """
        Delete this stack.
        """
        return self._client.stacks.delete(self.id)


class Stack(Config, ReprMixin, BaseStack):

    table_columns = ('id', '_name', 'distro', '_description')
    table_header = ('ID', 'Name', 'Distro', 'Description')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    description = Field(six.text_type)
    links = ListField(Link)
    distro = Field(six.text_type, required=True, help='Distribution ID')
    services = ListField(StackService, required=True,
                         help='See: :class:`StackService`')

    @property
    def _name(self):
        return '\n'.join(textwrap.wrap(self.name, 25))

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 30))


@prettify('node_groups', 'services')
class StackDetail(Stack, ReprMixin, BaseStack):

    __inherits__ = [Stack]

    table_columns = ('id', 'name', 'distro', 'created', '_description',
                     '_services', '_node_group_ids')
    table_header = ('ID', 'Name', 'Distro', 'Created', 'Description',
                    'Services', 'Node Groups')

    created = Field(DateTime, required=True,
                    help=':py:class:`~datetime.datetime` corresponding to '
                         'creation date')
    node_groups = ListField(StackNodeGroup, required=True,
                            help='See: :class:`StackNodeGroup`')

    def display(self):
        display_result(self, StackDetail, title='Stack')

        if self.node_groups:
            display_result(self.node_groups, StackNodeGroup,
                           title='Node Groups')

            self._display_components()

    def _display_components(self):
        rows = []
        for group in self.node_groups:
            group_column = chain([group.id], repeat(''))
            rows.extend(
                no_nulls((grp, comp['name']))
                for grp, comp in six.moves.zip(group_column, group.components)
            )

        print_table(rows, ('Node Group', 'Name'), title='Components')

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 60))

    @property
    def _node_group_ids(self):
        return '\n'.join(
            textwrap.wrap(', '.join(group.id for group in self.node_groups))
        )


class Distro(Config, ReprMixin):

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    version = Field(six.text_type, required=True)


@prettify('services')
class DistroDetail(Config, ReprMixin):

    table_columns = ('id', 'name', 'version')
    table_header = ('ID', 'Name', 'Version')

    __inherits__ = [Distro]

    services = ListField(DistroService, required=True,
                         help='See: :class:`DistroService`')

    def display(self):
        display_result(self, DistroDetail, title='Distro')
        six.print_()
        display_result(self.services, DistroService, 'Services')


class Script(Config, ReprMixin):

    table_columns = ('id', 'name', 'type', 'is_public', 'created', 'url')
    table_header = ('ID', 'Name', 'Type', 'Public', 'Created', 'URL')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    type = Field(six.text_type, required=True)
    url = Field(six.text_type, required=True)
    is_public = Field(bool, required=True)
    created = Field(DateTime, required=True,
                    help=':py:class:`~datetime.datetime` corresponding to '
                         'creation date')
    updated = Field(DateTime, required=True,
                    help=':py:class:`~datetime.datetime` corresponding to '
                         'date last updated')
    links = ListField(Link)

    def update(self, **kwargs):
        """
        Update this script. See
        :meth:`~lavaclient.api.scripts.Resource.update`.
        """
        return self._client.scripts.update(self.id, **kwargs)

    def delete(self):
        """
        Delete this script. See
        :meth:`~lavaclient.api.scripts.Resource.delete`.
        """
        return self._client.scripts.delete(self.id)


class Workload(Config, ReprMixin):

    table_columns = ('id', 'name', 'caption', '_description')
    table_header = ('ID', 'Name', 'Caption', 'Description')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    caption = Field(six.text_type, required=True)
    description = Field(six.text_type, required=True)

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 30))

    def recommendations(self, *args):
        """
        recommendations(storage_size, persistence)

        Get recommendations for this workload. See
        :meth:`~lavaclient.api.workloads.Resource.recommendations`.
        """
        return self._client.workloads.recommendations(self.id, *args)


class Size(Config, ReprMixin):

    table_columns = ('flavor', 'minutes', 'nodecount', 'recommended')
    table_header = ('Flavor', 'Minutes', 'Nodes', 'Recommended')

    flavor_id = Field(six.text_type, required=True, key='flavor')
    minutes = Field(float, required=True)
    nodecount = Field(int, required=True)
    recommended = Field(bool, default=False)


@prettify('requires')
class Recommendations(Config, ReprMixin):

    """Recommendations on how to use the Lava API for a given workload"""

    name = Field(six.text_type, required=True)
    description = Field(six.text_type, required=True)
    requires = ListField(six.text_type, required=True)
    sizes = ListField(Size, required=True,
                      help='See: :class:`Size`')

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 30))


class CredentialType(Config, ReprMixin):

    type = Field(six.text_type, required=True)
    schema = Field(dict, required=True)
    links = ListField(Link)


class SSHKey(Config, ReprMixin):

    table_columns = ('type', 'name')
    table_header = ('Type', 'Name')

    type = 'SSH Key'
    name = Field(six.text_type, key='key_name', required=True)

    @property
    def id(self):
        """Equivalent to :attr:`name`"""
        return self.name

    def delete(self):
        """Delete this key"""
        self._client.credentials.delete_ssh_key(self.name)


class CloudFilesCredential(Config, ReprMixin):

    table_columns = ('type', 'username')
    table_header = ('Type', 'Username')

    type = 'Cloud Files'
    username = Field(six.text_type, required=True)

    @property
    def id(self):
        """Equivalent to :attr:`username`"""
        return self.username

    def delete(self):
        """Delete this credential"""
        self._client.credentials.delete_cloud_files(self.username)


class S3Credential(Config, ReprMixin):

    table_columns = ('type', 'access_key_id')
    table_header = ('Type', 'Access Key ID')

    type = 'Amazon S3'
    access_key_id = Field(six.text_type, required=True)

    @property
    def id(self):
        """Equivalent to :attr:`access_key_id`"""
        return self.access_key_id

    def delete(self):
        """Delete s3 credential"""
        self.__client.credentials.delete_s3(self.access_key_id)


class AmbariCredential(Config, ReprMixin):

    table_columns = ('type', 'username')

    type = 'Ambari'
    username = Field(six.text_type, required=True)

    @property
    def id(self):
        """Equivalent to :attr:`username`"""
        return self.username

    def delete(self):
        """Delete s3 credential"""
        self.__client.credentials.delete_ambari(self.username)


class Credentials(Config, ReprMixin):

    cloud_files = ListField(CloudFilesCredential)
    ssh_keys = ListField(SSHKey)
    s3 = ListField(S3Credential)
    ambari = ListField(AmbariCredential)

    def display(self):
        data = chain(
            [('SSH Key', key.name) for key in self.ssh_keys],
            [('Cloud Files', cred.username) for cred in self.cloud_files],
            [('Amazon S3', cred.access_key_id) for cred in self.s3],
            [('Ambari', cred.username) for cred in self.ambari]
        )
        print_table(data, ('Type', 'Name'))


class AbsoluteLimit(Config, ReprMixin):

    limit = Field(int, required=True)
    remaining = Field(int, required=True)

    @property
    def used(self):
        return self.limit - self.remaining


class AbsoluteLimits(Config, ReprMixin):

    node_count = Field(AbsoluteLimit, required=True,
                       help='See: :class:`AbsoluteLimit`')
    ram = Field(AbsoluteLimit, required=True,
                help='See: :class:`AbsoluteLimit`')
    disk = Field(AbsoluteLimit, required=True,
                 help='See: :class:`AbsoluteLimit`')
    vcpus = Field(AbsoluteLimit, required=True,
                  help='See: :class:`AbsoluteLimit`')

    def display(self):
        properties = [
            ('Nodes', self.node_count.limit, self.node_count.remaining),
            ('RAM', self.ram.limit, self.ram.remaining),
            ('Disk', self.disk.limit, self.disk.remaining),
            ('VCPUs', self.vcpus.limit, self.vcpus.remaining),
        ]
        header = ('Property', 'Limit', 'Remaining')
        print_table(properties, header, title='Quotas')


class Limit(Config, ReprMixin):

    absolute = Field(AbsoluteLimits, required=True,
                     help='See: :class:`AbsoluteLimits`')
