import six
import logging
from figgis import Config, Field, ListField

from lavaclient2.api import resource
from lavaclient2 import constants


LOG = logging.getLogger(constants.LOGGER_NAME)


######################################################################
# API Responses
######################################################################

class Workload(Config):

    table_columns = ('id', 'name', 'caption', 'description')
    table_header = ('ID', 'Name', 'Caption', 'Description')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    caption = Field(six.text_type, required=True)
    description = Field(six.text_type, required=True)


class WorkloadsResponse(Config):

    """Response from /workloads"""

    workloads = ListField(Workload, required=True)


class Size(Config):

    flavor = Field(six.text_type, required=True)
    minutes = Field(float, required=True)
    nodecount = Field(int, required=True)
    recommended = Field(bool, default=False)


class Recommendations(Config):

    """Recommendations on how to use the Lava API for a given workload"""

    name = Field(six.text_type, required=True)
    description = Field(six.text_type, required=True)
    requires = ListField(six.text_type, required=True)
    sizes = ListField(Size, required=True)


class RecommendationsResponse(Config):

    recommendations = ListField(Recommendations)


######################################################################
# API Request data
######################################################################

class RecommendationParams(Config):

    storagesize = Field(float, required=True)
    persistent = Field(six.text_type, choices=('all', 'none', 'data'))


######################################################################
# API Resource
######################################################################

class Resource(resource.Resource):

    """Workloads API methods"""

    def get(self):
        """
        Get list of Lava workloads

        :returns: List of Workload objects
        """
        return self._parse_response(
            self._client._get('/workloads'),
            WorkloadsResponse,
            wrapper='workloads')

    def recommendations(self, workload_id, storage_size, persistent):
        """
        Get recommendations for the given workload.

        :param workload_id: Workload ID (see the :func:`get` method)
        :param storage_size: The desired amount of disk space (in GB)
        :param persistent: One of the following values:
            - 'data': persistent (large) data storage is required
            - 'all': persist data and your cluster servers
            - 'none': your data and clusters are ephemeral
        :returns: List of Recommendation objects
        """
        params = self._marshal_request({'storagesize': storage_size,
                                        'persistent': persistent},
                                       RecommendationParams)
        return self._parse_response(
            self._client._get('/workloads/{0}/recommendations'.format(
                workload_id), params=params),
            RecommendationsResponse,
            wrapper='recommendations')
