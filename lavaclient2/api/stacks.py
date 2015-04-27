import logging
import six
import json
from figgis import Config, ListField, Field

from lavaclient2.api import resource
from lavaclient2.api.response import Stack, StackDetail
from lavaclient2.validators import Length, List, Range
from lavaclient2.util import CommandLine, command, argument, display_table
from lavaclient2.log import NullHandler


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
    distro = Field(six.text_type, required=True,
                   validator=Length(min=1, max=255))
    services = ListField(Service, required=True)
    node_groups = ListField(NodeGroup)


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Flavors API methods"""

    @command
    @display_table(Stack)
    def list(self):
        """
        List all stacks

        :returns: list of Stack objects
        """
        return self._parse_response(
            self._client._get('stacks'),
            StacksResponse,
            wrapper='stacks')

    @command
    @display_table(StackDetail)
    def get(self, stack_id):
        """
        Get a specific stack

        :returns: A Stack object
        """
        return self._parse_response(
            self._client._get('stacks/{0}'.format(stack_id)),
            StackResponse,
            wrapper='stack')

    @command(
        node_groups=argument(
            '--node-groups', type=json.loads,
            help='Json string containing an array with the following '
                 'elements: {0}; Component is an array with the following '
                 'elements: {1}'.format(
                     NodeGroup._describe(),
                     Component._describe())),
        services=argument(
            'services', type=json.loads,
            help='Json string containing an array with the following '
                 'elements: {0}'.format(Service._describe()))
    )
    @display_table(StackDetail)
    def create(self, name, distro, services, node_groups=None):
        """
        Create a stack

        :param name: Stack name
        :param distro: Valid distro identifier
        :param services: List of services. Each should have a name and
                         optionally a list of modes
        :param node_groups: List of node groups for the cluster
        :returns: Same as :func:`get`
        """
        data = dict(
            name=name,
            distro=distro,
            services=services,
        )
        if node_groups:
            data.update(node_groups=node_groups)

        request_data = self._marshal_request(
            data, CreateStackRequest, wrapper='stack')

        return self._parse_response(
            self._client._post('stacks', json=request_data),
            StackResponse,
            wrapper='stack')

    @command
    def delete(self, stack_id):
        """
        Delete a stack
        """
        self._client._delete('stacks/{0}'.format(stack_id))
