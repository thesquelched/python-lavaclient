import logging
import six
from figgis import Config, ListField, Field

from lavaclient2.api import response, resource
from lavaclient2 import constants
from lavaclient2.validators import Length, List


LOG = logging.getLogger(constants.LOGGER_NAME)


######################################################################
# API Responses
######################################################################

class StackResponse(Config):

    stack = Field(response.Stack, required=True)


class StacksResponse(Config):

    stacks = ListField(response.Stack, required=True)


######################################################################
# API Requests
######################################################################

class CreateStackService(Config):

    name = Field(six.text_type, required=True,
                 validator=Length(min=1, max=255))
    modes = ListField(six.text_type,
                      validator=List(Length(min=1, max=255)))


class CreateStackRequest(Config):

    name = Field(six.text_type, required=True,
                 validator=Length(min=1, max=255))
    distro = Field(six.text_type, required=True,
                   validator=Length(min=1, max=255))
    services = ListField(CreateStackService, required=True)
    node_groups = ListField(response.NodeGroup)


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
        return self.parse_response(
            self._client._get('stacks'),
            StacksResponse,
            wrapper='stacks')

    def get(self, stack_id):
        """
        Get a specific stack

        :returns: A Stack object
        """
        return self.parse_response(
            self._client._get('stacks/{0}'.format(stack_id)),
            StackResponse,
            wrapper='stack')

    def create(self, name, distro, services=None, node_groups=None):
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
            services=services or [],
        )
        if node_groups:
            data.update(node_groups=node_groups)

        request_data = self.marshal_request(
            data, CreateStackRequest, wrapper='stack')

        return self.parse_response(
            self._client._post('stacks', data=request_data),
            StackResponse,
            wrapper='stack')

    def delete(self, stack_id):
        """
        Delete a stack
        """
        self._client._delete('stacks/{0}'.format(stack_id))
