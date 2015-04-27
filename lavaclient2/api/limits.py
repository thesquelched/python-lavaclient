import logging
from figgis import Config, Field

from lavaclient2.api import resource
from lavaclient2 import constants


LOG = logging.getLogger(constants.LOGGER_NAME)


######################################################################
# API Responses
######################################################################

class AbsoluteLimit(Config):

    limit = Field(int, required=True)
    remaining = Field(int, required=True)

    def __repr__(self):
        return 'AbsoluteLimit(limit={0}, remaining={1})'.format(
            self.limit, self.remaining)


class AbsoluteLimits(Config):

    node_count = Field(AbsoluteLimit, required=True)
    ram = Field(AbsoluteLimit, required=True)
    disk = Field(AbsoluteLimit, required=True)
    vcpus = Field(AbsoluteLimit, required=True)


class Limit(Config):

    absolute = Field(AbsoluteLimits, required=True)


class LimitsResponse(Config):

    """Response from /limits"""

    limits = Field(Limit, required=True)


######################################################################
# API Resource
######################################################################

class Resource(resource.Resource):

    """Limits API methods"""

    def get(self):
        """
        Get resource limits for the tenant.
        """
        return self._parse_response(
            self._client._get('/limits'),
            LimitsResponse,
            wrapper='limits')
