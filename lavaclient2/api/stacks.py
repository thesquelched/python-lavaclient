import logging
import six
from figgis import Config, ListField, Field

from lavaclient2.api import resource
from lavaclient2.api.response import Stack, StackDetail
from lavaclient2 import constants
from lavaclient2.validators import Length, List, Range


LOG = logging.getLogger(constants.LOGGER_NAME)


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


class Component(Config):

    name = Field(six.text_type, required=True,
                 validator=Length(min=1, max=255))


class NodeGroup(Config):

    id = Field(six.text_type, required=True, validator=Length(min=1, max=36))
    flavor_id = Field(six.text_type)
    count = Field(int, validator=Range(min=0, max=100))
    components = ListField(Component)


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

class Resource(resource.Resource):

    """Flavors API methods"""

    def list(self):
        """
        List all stacks

        :returns: list of Stack objects
        """
        return self._parse_response(
            self._client._get('stacks'),
            StacksResponse,
            wrapper='stacks')

    def get(self, stack_id):
        """
        Get a specific stack

        :returns: A Stack object
        """
        return self._parse_response(
            self._client._get('stacks/{0}'.format(stack_id)),
            StackResponse,
            wrapper='stack')

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
            self._client._post('stacks', data=request_data),
            StackResponse,
            wrapper='stack')

    def delete(self, stack_id):
        """
        Delete a stack
        """
        self._client._delete('stacks/{0}'.format(stack_id))
