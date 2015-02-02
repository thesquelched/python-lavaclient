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
from six import text_type
from dateutil.parser import parse as dateparse
from datetime import datetime

from lavaclient2 import validators


def DateTime(value):
    """Parse a datetime object from a string value"""
    if isinstance(value, datetime):
        return value

    return dateparse(value)


class NodeGroup(Config):

    id = Field(text_type, required=True,
               validator=validators.Length(min=1, max=255))
    count = Field(int, validator=validators.Range(min=1, max=100))
    flavor_id = Field(text_type)
    components = Field(dict, default={})


class Cluster(Config):

    id = Field(text_type, required=True)
    created = Field(DateTime, required=True)
    updated = Field(DateTime)
    name = Field(text_type)
    status = Field(text_type, required=True)
    stack_id = Field(text_type, required=True)

    node_groups = ListField(NodeGroup, default=[])


class ClustersResponse(Config):

    clusters = ListField(Cluster, default=[])
