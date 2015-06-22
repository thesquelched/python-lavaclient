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

"""
Get information about available Hadoop platform distributions, e.g.
Hortonworks Data Platform
"""

import six
import logging
from figgis import Config, ListField, Field

from lavaclient.api import resource
from lavaclient.api.response import Distro, DistroDetail
from lavaclient.util import CommandLine, command, display_table
from lavaclient.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


######################################################################
# API Responses
######################################################################

class DistroResponse(Config):

    distro = Field(DistroDetail, required=True)


class DistrosResponse(Config):

    distros = ListField(Distro, required=True)


######################################################################
# API Resource
######################################################################

@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Distros API methods"""

    @command(parser_options=dict(
        description='List all supported distributions',
    ))
    @display_table(Distro)
    def list(self):
        """
        List all distros

        :returns: list of :class:`~lavaclient.api.response.Distro` objects
        """
        return self._parse_response(
            self._client._get('/distros'),
            DistrosResponse,
            wrapper='distros')

    @command(parser_options=dict(
        description='Show a specific distribution in detail',
    ))
    @display_table(DistroDetail)
    def get(self, distro_id):
        """
        Get a specific distro

        :param distro_id: Distribution ID
        :returns: :class:`~lavaclient.api.response.DistroDetail`
        """
        return self._parse_response(
            self._client._get('/distros/{0}'.format(distro_id)),
            DistroResponse,
            wrapper='distro')
