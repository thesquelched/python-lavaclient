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
from figgis import Config, Field, ListField
from dateutil.parser import parse as dateparse
from datetime import datetime

from lavaclient.validators import Length, Range
from lavaclient.util import display_result, prettify, _prettify, ssh_to_host
from lavaclient.log import NullHandler
from lavaclient import error


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


def DateTime(value):
    """Parse a datetime object from a string value"""
    if isinstance(value, datetime):
        return value

    return dateparse(value)


class IdReprMixin(object):

    def __repr__(self):
        return "{0}(id='{1}')".format(self.__class__.__name__, self.id)


class Link(Config):

    rel = Field(six.text_type, required=True)
    href = Field(six.text_type, required=True)

    def __repr__(self):
        return "Link(rel='{0}', href='{1}')".format(
            self.rel, self.href)


class Address(Config):

    address = Field(six.text_type, required=True, key='addr')
    version = Field(six.text_type, required=True)


class Addresses(Config):

    public = ListField(Address, required=True)
    private = ListField(Address, required=True)


@prettify('components')
class Node(Config, IdReprMixin):
    table_columns = ('id', 'name', 'node_group', 'status',
                     'public_ip', 'private_ip', '_components')
    table_header = ('ID', 'Name', 'Role', 'Status', 'Public IP',
                    'Private IP', 'Components')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    created = Field(DateTime, required=True)
    updated = Field(DateTime, required=True)
    status = Field(six.text_type, required=True)
    flavor_id = Field(six.text_type, required=True)
    addresses = Field(Addresses, required=True)
    node_group = Field(six.text_type, required=True)
    components = ListField(dict, required=True)

    @property
    def private_ip(self):
        try:
            return self.addresses.private[0].address
        except IndexError:
            return None

    @property
    def public_ip(self):
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
        :returns: Output from running command
        """
        return self._ssh(username, command=command, ssh_command=ssh_command)


@prettify('components')
class NodeGroup(Config, IdReprMixin):

    table_columns = ('id', 'flavor_id', 'count', '_components')
    table_header = ('ID', 'Flavor', 'Count', 'Components')

    id = Field(six.text_type, required=True,
               validator=Length(min=1, max=255))
    count = Field(int, validator=Range(min=1, max=100))
    flavor_id = Field(six.text_type)
    components = ListField(dict, default={})


class ClusterScript(Config):

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    status = Field(six.text_type, required=True)


class BaseCluster(object):

    @property
    def nodes(self):
        return self._client.clusters.nodes(self.id)

    def refresh(self):
        """
        Refresh the cluster. If this object was returned from
        :meth:`Lava.clusters.list`, it will return the same amount of detail
        as :meth:`Lava.clusters.get`.

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
        Wait for this cluster to become active

        :returns: :class:`ClusterDetail`
        """
        return self._client.clusters.wait(self.id, **kwargs)

    def ssh_proxy(self, **kwargs):
        """
        Start a SOCKS5 proxy over SSH to this cluster. See
        :meth:`Lava.clusters.wait`.
        """
        return self._client.clusters.ssh_proxy(self.id, **kwargs)

    def execute_on_node(self, node_name, command, **kwargs):
        """
        Execute a command on a cluster node. See:
        :meth:`Lava.clusters.ssh_execute`.
        """
        return self._client.clusters.ssh_execute(self.id, node_name, command,
                                                 **kwargs)


class Cluster(Config, IdReprMixin, BaseCluster):

    table_columns = ('id', 'name', 'status', 'stack_id', 'created')
    table_header = ('ID', 'Name', 'Status', 'Stack', 'Created')

    id = Field(six.text_type, required=True)
    created = Field(DateTime, required=True)
    updated = Field(DateTime, required=True)
    name = Field(six.text_type, required=True)
    status = Field(six.text_type, required=True)
    stack_id = Field(six.text_type, required=True)
    cbd_version = Field(int, required=True)
    links = ListField(Link, required=True)


class ClusterDetail(Config, IdReprMixin, BaseCluster):

    __inherits__ = [Cluster]

    table_columns = ('id', 'name', 'status', 'stack_id', 'created',
                     'cbd_version', 'username', 'progress')
    table_header = ('ID', 'Name', 'Status', 'Stack', 'Created', 'CBD Version',
                    'Username', 'Progress')

    node_groups = ListField(NodeGroup, required=True)
    username = Field(six.text_type, required=True)
    scripts = ListField(ClusterScript, required=True)
    progress = Field(float, required=True)

    def display(self):
        display_result(self, ClusterDetail, title='Cluster')

        if self.node_groups:
            six.print_()
            display_result(self.node_groups, NodeGroup, title='Node Groups')

        if self.scripts:
            six.print_()
            display_result(self.scripts, ClusterScript, title='Scripts')


class Flavor(Config, IdReprMixin):

    table_columns = ('id', 'name', 'ram', 'vcpus', 'disk')
    table_header = ('ID', 'Name', 'RAM', 'VCPUs', 'Disk')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    disk = Field(int, required=True)
    vcpus = Field(int, required=True)
    ram = Field(int, required=True)
    links = ListField(Link, required=True)


class ServiceComponent(Config):

    name = Field(six.text_type, required=True)
    mode = Field(six.text_type)


class DistroServiceMode(Config):

    name = Field(six.text_type, required=True)


@prettify('components')
class DistroService(Config):

    table_columns = ('name', 'version', '_components', '_description')
    table_header = ('Name', 'Version', 'Components', 'Description')

    name = Field(six.text_type, required=True)
    version = Field(six.text_type, required=True)
    description = Field(six.text_type, required=True)
    components = ListField(dict, required=True)

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 30))


class ResourceLimits(Config):

    max_count = Field(int, required=True)
    min_count = Field(int, required=True)
    min_ram = Field(int, required=True)


@prettify('components', 'resource_limits')
class StackNodeGroup(Config, IdReprMixin):

    table_columns = ('id', 'flavor_id', 'count', 'resource_limits.min_ram',
                     'resource_limits.min_count',
                     'resource_limits.max_count')
    table_header = ('ID', 'Flavor', 'Count', 'Min RAM', 'Min count',
                    'Max Count')

    id = Field(six.text_type, required=True)
    flavor_id = Field(six.text_type, required=True)
    resource_limits = Field(ResourceLimits, required=True)
    count = Field(int, required=True)
    components = ListField(dict, required=True)


class StackService(Config):

    name = Field(six.text_type, required=True)
    modes = ListField(six.text_type, required=True)


class BaseStack(object):

    def refresh(self):
        """
        Refresh this stack. If this object was returned from
        :meth:`Lava.stacks.list`, it will return the same amount of detail as
        :meth:`Lava.stacks.get`.

        :returns: :class:`StackDetail`
        """
        return self._client.stacks.get(self.id)

    def delete(self):
        """
        Delete this stack.
        """
        return self._client.stacks.delete(self.id)


@prettify('services')
class Stack(Config, IdReprMixin, BaseStack):

    table_columns = ('id', 'name', 'distro', '_description', '_services')
    table_header = ('ID', 'Name', 'Distro', 'Description', 'Services')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    description = Field(six.text_type)
    links = ListField(Link, required=True)
    distro = Field(six.text_type, required=True)
    services = ListField(StackService, required=True)

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 50))


@prettify('node_groups')
class StackDetail(Stack, IdReprMixin, BaseStack):

    __inherits__ = [Stack]

    table_columns = ('id', 'name', 'distro', 'created', '_description',
                     '_services', '_node_group_ids')
    table_header = ('ID', 'Name', 'Distro', 'Created', 'Description',
                    'Services', 'Node Groups')

    created = Field(DateTime, required=True)
    node_groups = ListField(StackNodeGroup, required=True)

    def display(self):
        display_result(self, StackDetail, title='Stack')

        if self.node_groups:
            display_result(self.node_groups, StackNodeGroup,
                           title='Node Groups')

    @property
    def _node_group_ids(self):
        return _prettify([group.id for group in self.node_groups])


class Distro(Config, IdReprMixin):

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    version = Field(six.text_type, required=True)


@prettify('services')
class DistroDetail(Config, IdReprMixin):

    table_columns = ('id', 'name', 'version')
    table_header = ('ID', 'Name', 'Version')

    __inherits__ = [Distro]

    services = ListField(DistroService, required=True)

    def display(self):
        display_result(self, DistroDetail, title='Distro')
        six.print_()
        display_result(self.services, DistroService, 'Services')


class Script(Config, IdReprMixin):

    table_columns = ('id', 'name', 'type', 'is_public', 'created', 'url')
    table_header = ('ID', 'Name', 'Type', 'Public', 'Created', 'URL')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    type = Field(six.text_type, required=True)
    url = Field(six.text_type, required=True)
    is_public = Field(bool, required=True)
    created = Field(DateTime, required=True)
    updated = Field(DateTime, required=True)
    links = ListField(Link, required=True)

    def update(self, **kwargs):
        """
        Update this script. See :meth:`Lava.scripts.update`.
        """
        return self._client.scripts.update(self.id, **kwargs)

    def delete(self):
        """
        Delete this script.
        """
        return self._client.scripts.delete(self.id)


class Workload(Config):

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
        Get recommendations for this workload. See
        :meth:`Lava.workloads.recommendations`.
        """
        return self._client.workloads.recommendations(self.id, *args)


class Size(Config):

    table_columns = ('flavor', 'minutes', 'nodecount', 'recommended')
    table_header = ('Flavor', 'Minutes', 'Nodes', 'Recommended')

    flavor = Field(six.text_type, required=True)
    minutes = Field(float, required=True)
    nodecount = Field(int, required=True)
    recommended = Field(bool, default=False)


@prettify('requires')
class Recommendations(Config):

    """Recommendations on how to use the Lava API for a given workload"""

    name = Field(six.text_type, required=True)
    description = Field(six.text_type, required=True)
    requires = ListField(six.text_type, required=True)
    sizes = ListField(Size, required=True)

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 30))


class CredentialType(Config):

    type = Field(six.text_type, required=True)
    schema = Field(dict, required=True)
    links = ListField(Link, required=True)


class SSHKey(Config):

    table_columns = ('type', 'name')
    table_header = ('Type', 'Name')

    type = 'SSH Key'
    name = Field(six.text_type, key='key_name', required=True)

    def delete(self):
        """Delete this key"""
        self._client.credentials.delete_ssh_key(self.name)


class CloudFilesCredential(Config):

    table_columns = ('type', 'username')
    table_header = ('Type', 'Username')

    type = 'Cloud Files'
    username = Field(six.text_type, required=True)

    def delete(self):
        """Delete this credential"""
        self._client.credentials.delete_cloud_files(self.username)


class S3Credential(Config):

    table_columns = ('type', 'access_key_id')
    table_header = ('Type', 'Access Key ID')

    type = 'Amazon S3'
    access_key_id = Field(six.text_type, required=True)

    def delete(self):
        """Delete s3 credential"""
        self.__client.credentials.delete_s3(self.access_key_id)
