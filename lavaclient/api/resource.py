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
import figgis
import six

from lavaclient import error
from lavaclient.log import NullHandler
from lavaclient.util import inject_client


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


def _prune_marshaled_data(marshaled, original_data):
    """Prune keys from marshaled data that don't exist in the original data
    (which would have been put there by to_dict method.

    WARNING: Modifies the marshaled data
    """
    for key, value in list(marshaled.items()):
        if key not in original_data:
            del marshaled[key]
            continue

        if isinstance(value, dict):
            _prune_marshaled_data(value, original_data[key])
        elif isinstance(value, (list, tuple)):
            for item, orig_item in zip(value, original_data[key]):
                if isinstance(item, dict):
                    _prune_marshaled_data(item, orig_item)

    return marshaled


class Resource(object):

    def __init__(self, client, cli_args=None):
        self._client = client
        self._args = cli_args
        self._command_line = cli_args is not None

    def _parse_response(self, data, response_class, wrapper=None):
        """
        Parse json data using the response class, returning
        response_class(data).  If wrapper is not None, return the attribute in
        wrapper instead of the object itself.

        After parsing the data, the client object is injected into any Config
        objects. This allows Config objects to potentially make further API
        queries.
        """
        if wrapper is not None and not hasattr(response_class, wrapper):
            raise AttributeError('{0} does not have attribute {1}'.format(
                response_class.__name__, wrapper))

        try:
            response = inject_client(self._client, response_class(data))
            return response if wrapper is None else response.get(wrapper)
        except (figgis.PropertyError, figgis.ValidationError) as exc:
            msg = 'Invalid response: {0}'.format(exc)
            LOG.critical(msg, exc_info=exc)
            raise error.ApiError(msg)

    def _marshal_request(self, data, request_class, wrapper=None):
        """
        Check that the json request body conforms to the request class, then
        return the unmodified data.  If wrapper is not None, wrap data in a
        dictionary with the wrapper as the key.
        """
        try:
            marshaled = _prune_marshaled_data(request_class(data).to_dict(),
                                              data)
            return marshaled if wrapper is None else {wrapper: marshaled}
        except (figgis.PropertyError, figgis.ValidationError) as exc:
            msg = 'Invalid request data: {0}'.format(exc)
            LOG.critical(msg, exc_info=exc)
            raise error.InvalidError(msg)

    def _cli_printer(self, logger=None):
        """Create a function that logs the messages send to it, then prints
        them to stdout if the command line is enabled"""
        if logger is None:
            logger = LOG

        def printer(message, level=None, logger=logger):
            if level is None:
                level = logging.DEBUG

            logger.log(level, message)
            if self._command_line:
                six.print_(message)

        return printer
