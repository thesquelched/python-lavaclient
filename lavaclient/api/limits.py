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
from figgis import Config, Field

from lavaclient.api import resource
from lavaclient.util import CommandLine, command, display_table
from lavaclient.log import NullHandler
from lavaclient.api.response import AbsoluteLimits, Limit


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class LimitsResponse(Config):

    """Response from /limits"""

    limits = Field(Limit, required=True)


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Limits API methods"""

    @command(parser_options=dict(
        description='Get resource limits for the authenticated user',
    ))
    @display_table(AbsoluteLimits)
    def get(self):
        """
        Get resource limits for the tenant.

        :returns: :class:`AbsoluteLimits`
        """
        resp = self._parse_response(
            self._client._get('/limits'),
            LimitsResponse,
            wrapper='limits')
        return resp.absolute
