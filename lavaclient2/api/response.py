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

from lavaclient2 import validators


def DateTime(value):
    """Parse a datetime object from a string value"""
    if isinstance(value, datetime):
        return value

    return dateparse(value)


class IdReprMixin(object):

    def __repr__(self):
        return "{0}(id='{1}')".format(self.__class__.__name__, self.id)


class NodeGroup(Config, IdReprMixin):

    id = Field(six.text_type, required=True,
               validator=validators.Length(min=1, max=255))
    count = Field(int, validator=validators.Range(min=1, max=100))
    flavor_id = Field(six.text_type)
    components = Field(dict, default={})


class Cluster(Config, IdReprMixin):

    id = Field(six.text_type, required=True)
    created = Field(DateTime, required=True)
    updated = Field(DateTime)
    name = Field(six.text_type)
    status = Field(six.text_type, required=True)
    stack_id = Field(six.text_type, required=True)

    node_groups = ListField(NodeGroup, default=[])


class Link(Config):

    rel = Field(six.text_type, required=True)
    href = Field(six.text_type, required=True)

    def __repr__(self):
        return "Link(rel='{0}', href='{1}')".format(
            self.rel, self.href)
