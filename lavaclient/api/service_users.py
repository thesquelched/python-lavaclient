import logging
import six
from figgis import Config, ListField, Field

from lavaclient.api import resource
from lavaclient import constants
from lavaclient.api.response import ServiceUser, ServiceUserDetail
from lavaclient.util import command, display_table, CommandLine

LOG = logging.getLogger(constants.LOGGER_NAME)


######################################################################
# API Responses
######################################################################

class ServiceUsersResponse(Config):

    """Response from GET /clusters/<cluster_id>/service_users"""

    service_users = ListField(ServiceUser, required=True)


class ServiceUserResponse(Config):

    """Response from PUT /clusters/<cluster_id>/service_users"""

    service_user = Field(ServiceUserDetail, required=True)


######################################################################
# API Requests
######################################################################

class ResetRequest(Config):

    service = Field(six.text_type, required=True, choices=['AMBARI'])
    username = Field(six.text_type, required=True)


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Service users API methods"""

    @command(parser_options=dict(
        description='List all service users in a cluster'
    ))
    @display_table(ServiceUser)
    def list(self, cluster_id):
        """
        List service users belonging to the cluster.

        :returns: List of :class:`~lavaclient.api.response.ServiceUser` objects
        """
        return self._parse_response(
            self._client._get('clusters/{0}/service_users'.format(cluster_id)),
            ServiceUsersResponse,
            wrapper='service_users')

    @command(parser_options=dict(
        description='Reset password for Ambari read-only user'
    ))
    @display_table(ServiceUserDetail)
    def reset_ambari_password(self, cluster_id):
        """
        Reset password for Ambari read-only user on cluster.

        :returns: :class:`~lavaclient.api.response.ServiceUserDetail`
        """
        data = {'service': 'AMBARI',
                'username': self._client._username}

        request_data = self._marshal_request(
            data, ResetRequest, wrapper='service_user')

        return self._parse_response(
            self._client._put('clusters/{0}/service_users'.format(cluster_id),
                              json=request_data),
            ServiceUserResponse,
            wrapper='service_user')
