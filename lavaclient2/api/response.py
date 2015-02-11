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


from figgis import Config, Field, ListField
import six
from dateutil.parser import parse as dateparse
from datetime import datetime

from lavaclient2.validators import Length, Range


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


class Node(Config, IdReprMixin):

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    created = Field(DateTime, required=True)
    updated = Field(DateTime, required=True)
    role = Field(six.text_type, required=True)
    status = Field(six.text_type, required=True)
    ip = Field(six.text_type, required=True)
    fqdn = Field(six.text_type, required=True)
    flavor_id = Field(six.text_type, required=True)
    private_ip = Field(six.text_type, required=True)
    node_group = Field(six.text_type, required=True)


class NodeGroup(Config, IdReprMixin):

    id = Field(six.text_type, required=True,
               validator=Length(min=1, max=255))
    count = Field(int, validator=Range(min=1, max=100))
    flavor_id = Field(six.text_type)
    components = Field(dict, default={})


class Cluster(Config, IdReprMixin):

    id = Field(six.text_type, required=True)
    created = Field(DateTime, required=True)
    updated = Field(DateTime)
    name = Field(six.text_type)
    status = Field(six.text_type, required=True)
    stack_id = Field(six.text_type, required=True)
    links = ListField(Link, required=True)

    node_groups = ListField(NodeGroup, default=[])


class Flavor(Config, IdReprMixin):

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    disk = Field(int, required=True)
    vcpus = Field(int, required=True)
    ram = Field(int, required=True)
    links = ListField(Link, required=True)


class ServiceComponent(Config):

    name = Field(six.text_type, required=True)
    mode = Field(six.text_type)


class BaseService(Config):

    name = Field(six.text_type, required=True)
    version = Field(six.text_type, required=True)
    components = ListField(ServiceComponent, required=True)


class StackService(Config):

    __inherits__ = [BaseService]

    modes = ListField(six.text_type)


class DistroServiceMode(Config):

    name = Field(six.text_type, required=True)


class DistroService(Config):

    __inherits__ = [BaseService]

    description = Field(six.text_type, required=True)
    modes = ListField(DistroServiceMode)


class Stack(Config, IdReprMixin):

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    distro = Field(six.text_type, required=True)
    services = ListField(StackService, required=True)
    node_groups = ListField(NodeGroup)


class Distro(Config, IdReprMixin):

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    version = Field(six.text_type, required=True)
    services = ListField(DistroService, required=True)
