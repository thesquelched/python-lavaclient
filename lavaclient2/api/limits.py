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

from lavaclient2.api import resource
from lavaclient2.util import (CommandLine, command, display_table,
                              print_table)
from lavaclient2.log import NullHandler


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


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

    def display(self):
        data = self.absolute

        properties = [
            ('Nodes', data.node_count.limit, data.node_count.remaining),
            ('RAM', data.ram.limit, data.ram.remaining),
            ('Disk', data.disk.limit, data.disk.remaining),
            ('VCPUs', data.vcpus.limit, data.vcpus.remaining),
        ]
        header = ('Property', 'Limit', 'Remaining')
        print_table(properties, header, title='Quotas')


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
    @display_table(Limit)
    def get(self):
        """
        Get resource limits for the tenant.
        """
        return self._parse_response(
            self._client._get('/limits'),
            LimitsResponse,
            wrapper='limits')
