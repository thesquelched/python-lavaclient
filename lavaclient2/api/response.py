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

import textwrap
import six
from figgis import Config, Field, ListField
from dateutil.parser import parse as dateparse
from datetime import datetime

from lavaclient2.validators import Length, Range
from lavaclient2.util import display_result, prettify, _prettify


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


@prettify('components')
class NodeGroup(Config, IdReprMixin):

    table_columns = ('id', 'flavor_id', 'count', '_components')
    table_header = ('ID', 'Flavor', 'Count', 'Components')

    id = Field(six.text_type, required=True,
               validator=Length(min=1, max=255))
    count = Field(int, validator=Range(min=1, max=100))
    flavor_id = Field(six.text_type)
    components = ListField(dict, default={})


class Cluster(Config, IdReprMixin):

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


class ClusterScript(Config):

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    status = Field(six.text_type, required=True)


class ClusterDetail(Config, IdReprMixin):

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


@prettify('services')
class Stack(Config, IdReprMixin):

    table_columns = ('id', 'name', 'distro', '_services')
    table_header = ('ID', 'Name', 'Distro', 'Services')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    links = ListField(Link, required=True)
    distro = Field(six.text_type, required=True)
    services = ListField(StackService, required=True)


@prettify('node_groups')
class StackDetail(Stack):

    __inherits__ = [Stack]

    table_columns = ('id', 'name', 'distro', 'created', '_services',
                     '_node_group_ids')
    table_header = ('ID', 'Name', 'Distro', 'Created', 'Services',
                    'Node Groups')

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
