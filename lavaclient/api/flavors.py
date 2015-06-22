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

import six
import logging
from figgis import Config, ListField

from lavaclient.api import resource
from lavaclient.api.response import Flavor
from lavaclient.util import CommandLine, command, display_table
from lavaclient.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class FlavorsResponse(Config):

    flavors = ListField(Flavor, required=True)


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Flavors API methods"""

    @command(parser_options=dict(
        description='List all node flavors',
    ))
    @display_table(Flavor)
    def list(self):
        """
        List all flavors

        :returns: List of :class:`~lavaclient.api.response.Flavor` objects
        """
        return self._parse_response(
            self._client._get('/flavors'),
            FlavorsResponse,
            wrapper='flavors')
