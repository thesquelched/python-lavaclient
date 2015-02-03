import logging
import figgis

from lavaclient2 import error
from lavaclient2 import constants


LOG = logging.getLogger(constants.LOGGER_NAME)


class ApiMethod(object):

    def parse_response(self, data, response_class, wrapper=None):
        if wrapper is not None and not hasattr(response_class, wrapper):
            raise AttributeError('{0} does not have attribute {1}'.format(
                response_class.__name__, wrapper))

        try:
            response = response_class(data)
            return response if wrapper is None else response.get(wrapper)
        except (figgis.PropertyError, figgis.ValidationError) as exc:
            msg = 'Invalid response: {0}'.format(exc)
            LOG.critical(msg, exc_info=exc)
            raise error.ApiError(msg)
