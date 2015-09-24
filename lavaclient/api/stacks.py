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
import six
from collections import defaultdict
from figgis import Config, ListField, Field

from lavaclient.api import resource
from lavaclient.api.response import Stack, StackDetail
from lavaclient.validators import Length, List, Range
from lavaclient.util import (CommandLine, command, display_table, argument,
                             read_json, confirm, display_result, print_table,
                             display, table_data)
from lavaclient.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class StackResponse(Config):

    stack = Field(StackDetail, required=True)


class StacksResponse(Config):

    stacks = ListField(Stack, required=True)


######################################################################
# API Requests
######################################################################

class Service(Config):

    name = Field(six.text_type, required=True,
                 validator=Length(min=1, max=255))
    modes = ListField(six.text_type,
                      validator=List(Length(min=1, max=255)))

    @classmethod
    def _describe(cls):
        return cls.describe().replace('\n', ', ')


class Component(Config):

    name = Field(six.text_type, required=True,
                 validator=Length(min=1, max=255))

    @classmethod
    def _describe(cls):
        return cls.describe().replace('\n', ', ')


class NodeGroup(Config):

    id = Field(six.text_type, required=True, validator=Length(min=1, max=36))
    flavor_id = Field(six.text_type)
    count = Field(int, validator=Range(min=0, max=100))
    components = ListField(Component)

    @classmethod
    def _describe(cls):
        return cls.describe().replace('\n', ', ')


class CreateStackRequest(Config):

    name = Field(six.text_type, required=True,
                 validator=Length(min=1, max=255))
    description = Field(six.text_type,
                        validator=Length(min=1, max=1024))
    distro = Field(six.text_type, required=True,
                   validator=Length(min=1, max=255))
    services = ListField(Service, required=True)
    node_groups = ListField(NodeGroup)


######################################################################
# API Resource
######################################################################

def indent(value, width=4):
    if not value:
        return value

    lines = value.split('\n')
    return '\n'.join(' ' * width + line for line in lines)


SERVICE_CREATE_EPILOG = """\
SERVICES

Each cluster has a number of services installed, e.g. HDFS, Oozie, Hive, etc.
When creating a custom stack, you must indicate which services you want to be
installed. You can see a list of services available in a certain distribution
using the following command:

    lava distros get <distro_id>

To specify the services you want to be included with your stack, you must pass
in a valid JSON string containing a list of services, with each service being
a JSON object in the following format:

{services}

Here is an example of a valid service list:

    [{{"name": "HDFS", "modes": ["Secondary"]}},
     {{"name": "YARN"}},
     {{"name": "MapReduce"}}]

NODE GROUPS

Each service is comprised of one or more components. To create a custom stack,
you must specify where each component should be installed by creating node
groups. In addition to components, you can also control the node flavor and
the number of nodes to create. For each service you include in your stack, you
should include each service component in a node group.

Like with services, node groups must be a string with valid JSON data,
representing a list of JSON objects in the following format:

{node_groups}

Here's an example with two node groups:

    [{{"id": "master", "count": 1, "flavor_id": "hadoop1-7",
      "components": [{{"name": "Namenode"}}, {{"name": "ResourceManager"}}]}},
     {{"id": "slave",
      "components": [{{"name": "NodeManager"}}]}}]
""".format(services=indent(Service.describe()),
           node_groups=indent(NodeGroup.describe()))


def display_stack_services(result):
    service_stacks = defaultdict(set)
    for stack in result:
        for service in stack.services:
            service_stacks[service.name].add(stack.id)

    header = [''] + [six.text_type(i + 1)
                     for i in six.moves.range(len(result))]

    sorted_services = [(service, service_stacks[service])
                       for service in sorted(service_stacks)]
    rows = [
        [service] + ['X' if stack.id in svc_stacks else '' for stack in result]
        for service, svc_stacks in sorted_services]

    print_table(rows, header, title='Services')


def display_stacks(result):
    data, header = table_data(result, Stack)
    header = [''] + list(header)
    data = [[i] + list(row) for i, row in enumerate(data, start=1)]

    print_table(data, header, title='Stacks')
    display_stack_services(result)


@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Flavors API methods"""

    @command(parser_options=dict(
        description='List all existing stacks',
    ))
    @display(display_stacks)
    def list(self):
        """
        List all stacks

        :returns: List of :class:`~lavaclient.api.response.Stack` objects
        """
        return self._parse_response(
            self._client._get('stacks'),
            StacksResponse,
            wrapper='stacks')

    @command(parser_options=dict(
        description='Show a specific stack in detail',
    ))
    @display_table(StackDetail)
    def get(self, stack_id):
        """
        Get a specific stack

        :param stack_id: Stack ID
        :returns: :class:`~lavaclient.api.response.StackDetail`
        """
        return self._parse_response(
            self._client._get('stacks/{0}'.format(stack_id)),
            StackResponse,
            wrapper='stack')

    @command(
        parser_options=dict(
            description='Create a custom stack',
            epilog=SERVICE_CREATE_EPILOG,
        ),
        name=argument(help='A stack identifier, e.g. MY_HADOOP_STACK'),
        distro=argument(help='An existing distribution ID; see '
                             '`lava distros list`'),
        services=argument(type=read_json,
                          help='JSON data string or path to file containing '
                               'JSON data; see SERVICES'),
        node_groups=argument(type=read_json,
                             help='JSON data string or p ath to file '
                                  'containing JSON data; see NODE GROUPS'),
        description=argument(help='A brief description of the purpose '
                                  'of the stack')
    )
    @display_table(StackDetail)
    def create(self, name, distro, services, node_groups=None,
               description=None):
        """
        Create a stack

        :param name: Stack name
        :param distro: Valid distro identifier
        :param services: List of services. Each should have a name and
                         optionally a list of modes
        :param node_groups: List of node groups for the cluster
        :returns: :class:`~lavaclient.api.response.StackDetail`
        """
        data = dict(
            name=name,
            distro=distro,
            services=services,
        )
        if node_groups:
            data.update(node_groups=node_groups)
        if description:
            data.update(description=description)

        request_data = self._marshal_request(
            data, CreateStackRequest, wrapper='stack')

        return self._parse_response(
            self._client._post('stacks', json=request_data),
            StackResponse,
            wrapper='stack')

    @command(
        parser_options=dict(description='Delete a custom stack'),
        force=argument(action='store_true',
                       help='Do not show confirmation dialog'),
    )
    def _delete(self, stack_id, force=False):
        if not force:
            display_result(self.get(stack_id), StackDetail)

            if not confirm('Delete this stack?'):
                return

        self.delete(stack_id)

    def delete(self, stack_id):
        """
        Delete a stack

        :param stack_id: Stack ID
        """
        self._client._delete('stacks/{0}'.format(stack_id))
