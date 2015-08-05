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

import argparse
import six
import sys
import getpass
import logging
import os
import figgis

from lavaclient._version import __version__
from lavaclient.client import Lava
from lavaclient.error import LavaError
from lavaclient.util import get_function_arguments, first_exists, table_data
from lavaclient.log import NullHandler
from lavaclient.api import (clusters, limits, flavors, stacks, distros,
                            scripts, nodes, credentials)


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


def create_client(args):
    """
    Create instance of Lava from CLI args
    """
    apikey = first_exists(args.lava_api_key,
                          os.environ.get('LAVA_API_KEY'),
                          os.environ.get('OS_API_KEY'))
    token = first_exists(args.token,
                         os.environ.get('LAVA_AUTH_TOKEN'),
                         os.environ.get('AUTH_TOKEN'))
    user = first_exists(args.user,
                        os.environ.get('LAVA_USERNAME'),
                        os.environ.get('OS_USERNAME'),
                        getpass.getuser())
    password = first_exists(args.password,
                            os.environ.get('LAVA_PASSWORD'),
                            os.environ.get('OS_PASSWORD'))

    if not any((apikey, token, password)):
        if args.headless:
            six.print_('Error: no API key, token, or password specified',
                       file=sys.stderr)
            sys.exit(1)
        else:
            password = getpass.getpass('Password for {0}: '.format(user))

    try:
        return Lava(
            user,
            api_key=apikey,
            token=token,
            password=password,
            tenant_id=first_exists(args.tenant,
                                   os.environ.get('LAVA_TENANT_NAME'),
                                   os.environ.get('OS_TENANT_NAME')),
            region=first_exists(args.region,
                                os.environ.get('LAVA_REGION_NAME'),
                                os.environ.get('OS_REGION_NAME')),
            auth_url=first_exists(args.auth_url,
                                  os.environ.get('LAVA_AUTH_URL'),
                                  os.environ.get('OS_AUTH_URL')),
            endpoint=first_exists(args.endpoint,
                                  os.environ.get('LAVA2_API_URL'),
                                  os.environ.get('LAVA_API_URL')),
            verify_ssl=args.verify_ssl,
            _cli_args=args)
    except LavaError as exc:
        six.print_('Error during authentication: {0}'.format(exc),
                   file=sys.stderr)
        if args.debug:
            raise

        sys.exit(1)


def lava_shell(client, args):
    """Start an embeded IPython shell with the client already defined"""
    try:
        from IPython.terminal.embed import InteractiveShellEmbed
    except ImportError:
        six.print_('ERROR: shell command requires ipython to be installed',
                   file=sys.stderr)
        sys.exit(1)

    shell = InteractiveShellEmbed(user_ns={'lava': client})
    shell("Lava client is stored in 'lava' variable")


def print_unformatted_table(args, result):
    result_list = [result] if isinstance(result, figgis.Config) else result
    response_class = result_list[0].__class__

    data, long_header = table_data(result, response_class)
    header = [item.replace(' ', '_').lower() for item in long_header]

    delim = six.text_type(args.delimiter)

    six.print_(delim.join(header),
               file=sys.stdout if args.show_header else sys.stderr)

    for row in data:
        six.print_(delim.join(six.text_type(item).replace(',', ' ')
                              for item in row))


def print_action(func, args, *f_args, **f_kwargs):
    if args.pretty_print and hasattr(func, 'display'):
        func.display(func.__self__, *f_args, **f_kwargs)
    else:
        result = func(*f_args, **f_kwargs)
        if not result:
            return

        if isinstance(result, figgis.Config) or (
                isinstance(result, (list, tuple)) and
                all(isinstance(item, figgis.Config) for item in result)):
            print_unformatted_table(args, result)
        else:
            six.print_(result)


def call_action(func, args):
    required, optional = get_function_arguments(func)

    f_args = [getattr(args, name) for name in required]
    f_kwargs = dict((name, getattr(args, name)) for name in optional)

    return print_action(func, args, *f_args, **f_kwargs)


def print_auth_token(client, args):
    """Print the authentication token"""
    six.print_('AUTH_TOKEN={0}'.format(client.token))


# Dispatch for non-API commands
COMMAND_DISPATCH = dict(
    shell=lava_shell,
    authenticate=print_auth_token,
)


def execute_command(client, args):
    """
    Execute lava command
    """
    resource = args.resource
    if resource == 'shell':
        args.enable_cli = False

    if resource in COMMAND_DISPATCH:
        COMMAND_DISPATCH[resource](client, args)
        sys.exit(0)

    method = args.method
    action = getattr(getattr(client, resource), method)

    call_action(action, args)


def initialize_logging(args):  # pragma: nocover
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

        # Do crazy verbose logging for HTTP connections
        if args.debug > 1:
            try:
                import http.client as http_client
            except ImportError:
                # Python 2
                import httplib as http_client

            http_client.HTTPConnection.debuglevel = 1
    try:
        logging.captureWarnings(True)
    except AttributeError:
        # Not present in python 2.6
        pass

    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('iso8601').setLevel(logging.CRITICAL)


def with_opposites(parser, dest, *options, **kwargs):
    """
    Generate a mutually exclusive group comprised of the option with the given
    strings and their opposites.

    For example, `with_opposites(p, 'foo', '--foo', '-f')` creates the
    following:

        --foo, -f: store true
        --no-foo, -F: store false
    """
    if 'dest' in kwargs or 'action' in kwargs:
        raise ValueError('dest and action options are not allowed')
    if 'help' not in kwargs:
        raise ValueError('help is required')

    helpstr = kwargs.pop('help')

    opposite = []
    for opt in options:
        if opt.startswith('--'):
            opposite.append('--no-' + opt.lstrip('-'))
        elif opt[0] == '-' and not opt[1:].startswith('-'):
            opposite.append(opt.upper())
        else:
            raise ValueError('Invalid option string format: {0}'.format(opt))

    parser.add_argument(*options, action='store_true', dest=dest, help=helpstr,
                        **kwargs)
    parser.add_argument(*opposite, action='store_false', dest=dest,
                        help='Opposite of {0}'.format(', '.join(options)),
                        **kwargs)


def parse_argv():
    pipe_out = not sys.stdout.isatty()

    # Suppress setting attributes on the namespace from subparser options if
    # they are not specified, which allows us to have the same general options
    # on all parsers/subparsers, making their order not matter.
    parser_base = argparse.ArgumentParser(add_help=False,
                                          argument_default=argparse.SUPPRESS)
    parser = argparse.ArgumentParser(prog='lava')

    for prs in (parser_base, parser):
        general = prs.add_argument_group('General Options')
        general.add_argument('--token',
                             help='Lava API authentication token')
        general.add_argument('--api-key', dest='lava_api_key',
                             help='Lava API key')
        general.add_argument('--region',
                             help='API region, e.g. DFW')
        general.add_argument('--tenant',
                             help='Tenant ID')
        general.add_argument('--version',
                             help='Print client version')
        general.add_argument('--debug', '-d', action='count',
                             help='Print debugging information; use multiple '
                                  'times for more verbose logging')
        general.add_argument('--endpoint',
                             help='API endpoint URL')
        general.add_argument('--auth-url',
                             help='Keystone endpoint URL')
        general.add_argument('--headless', action='store_true',
                             help='Do not request user input')
        general.add_argument('--user',
                             help='Keystone auth username')
        general.add_argument('--password',
                             help='Keystone auth password')
        general.add_argument('--insecure', '-k', action='store_false',
                             dest='verify_ssl',
                             help='Turn of SSL cert validation')

        fmt = prs.add_argument_group('Formatting Options')
        with_opposites(fmt, 'pretty_print', '--format', '-f',
                       help='Show a formatted table in the output')
        with_opposites(fmt, 'show_header', '--header',
                       help='When outputting an unformatted table, print the '
                            'header to stdout instead of stderr')
        fmt.add_argument('--delimiter', '-l',
                         help='Column delimiter to use when formatting is '
                              'disabled')

    # Ugly hack; add defaults only to main parser so as to not override values
    # via child parsers
    parser.set_defaults(enable_cli=True,
                        verify_ssl=not os.environ.get('LAVA_INSECURE'),
                        delimiter=',',
                        show_header=False,
                        pretty_print=not pipe_out)

    subparsers = parser.add_subparsers(title='Commands')

    for command, func in COMMAND_DISPATCH.items():
        (subparsers.add_parser(command, parents=[parser_base],
                               description=func.__doc__)
                   .set_defaults(resource=command, method=command))

    for module in (clusters, limits, flavors, stacks, distros, scripts, nodes,
                   credentials):
        name = module.__name__.split('.')[-1]
        subparser = subparsers.add_parser(name, parents=[parser_base])
        subparser.set_defaults(resource=name)
        module.Resource._add_arguments(parser_base, subparser)

    args = parser.parse_args()

    # Force re-authentication for the 'authenticate' method
    if args.resource == 'authenticate':
        args.token = None

    return args


def main():
    args = parse_argv()
    if args.version:
        six.print_('lavaclient version ' + __version__)
        sys.exit(0)

    initialize_logging(args)

    try:
        client = create_client(args)
    except Exception as exc:
        LOG.critical('Error while creating client', exc_info=exc)
        six.print_('ERROR: {0}'.format(exc), file=sys.stderr)
        sys.exit(1)

    try:
        execute_command(client, args)
    except Exception as exc:
        LOG.debug('Error while executing command', exc_info=exc)
        six.print_('ERROR: {0}'.format(exc), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':  # pragma: nocover
    main()
    sys.exit(0)
