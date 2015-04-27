import argparse
import six
import sys
import getpass
import logging
import os

from lavaclient2._version import __version__
from lavaclient2.client import Lava
from lavaclient2.error import LavaError
from lavaclient2.util import get_function_arguments, first_exists
from lavaclient2.log import NullHandler
from lavaclient2.api import (clusters, limits, flavors, stacks, distros,
                             workloads, scripts)


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


def create_client(args):
    """
    Create instance of Lava from CLI args
    """
    apikey = first_exists(args.api_key,
                          os.environ.get('OS_API_KEY'))
    token = first_exists(args.token,
                         os.environ.get('AUTH_TOKEN'))
    user = first_exists(args.user,
                        os.environ.get('OS_USERNAME'),
                        getpass.getuser())
    password = first_exists(args.password,
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
                                   os.environ.get('OS_TENANT_NAME')),
            region=first_exists(args.region,
                                os.environ.get('OS_REGION_NAME')),
            auth_url=first_exists(args.auth_url,
                                  os.environ.get('OS_AUTH_URL')),
            endpoint=first_exists(args.endpoint,
                                  os.environ.get('LAVA2_API_URL')),
            verify_ssl=args.verify_ssl)
    except LavaError as exc:
        six.print_('Error during authentication: {0}'.format(exc),
                   file=sys.stderr)
        if args.debug:
            raise

        sys.exit(1)


def print_action(func, *args, **kwargs):
    if hasattr(func, 'display'):
        func.display(func.__self__, *args, **kwargs)
    else:
        result = func(*args, **kwargs)
        if result is not None:
            six.print_(result)


def call_action(func, args):
    required, optional = get_function_arguments(func)

    f_args = [getattr(args, name) for name in required]
    f_kwargs = dict((name, getattr(args, name)) for name in optional)

    return print_action(func, *f_args, **f_kwargs)


def print_auth_token(client):
    six.print_('AUTH_TOKEN={0}'.format(client.token))


def execute_command(args):
    """
    Execute lava command
    """
    resource = args.resource
    command = args.command

    client = create_client(args)

    if resource == 'authenticate':
        print_auth_token(client)
        sys.exit(0)

    action = getattr(getattr(client, resource), command)

    try:
        call_action(action, args)
    except Exception as exc:
        LOG.debug('Error while calling action', exc_info=exc)
        six.print_('ERROR: {0}'.format(exc), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass


def initialize_logging(args):  # pragma: nocover
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

        # Do crazy verbose logging for HTTP connections
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


def parse_argv():
    parser_base = argparse.ArgumentParser(add_help=False)
    general = parser_base.add_argument_group('General Options')
    general.add_argument('--token',
                         help='Lava API authentication token')
    general.add_argument('--api-key',
                         help='Lava API key')
    general.add_argument('--region',
                         help='API region, e.g. DFW')
    general.add_argument('--tenant',
                         help='Tenand ID')
    general.add_argument('--version',
                         help='Print client version')
    general.add_argument('--debug', '-d', action='store_true',
                         help='Print debugging information')
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

    parser = argparse.ArgumentParser(prog='lava2', parents=[parser_base])
    subparsers = parser.add_subparsers(title='Commands')

    # Add 'authenticate' command
    (subparsers.add_parser('authenticate', parents=[parser_base])
               .set_defaults(resource='authenticate',
                             command='authenticate'))

    for module in (clusters, limits, flavors, stacks, distros, workloads,
                   scripts):
        name = module.__name__.split('.')[-1]
        subparser = subparsers.add_parser(name, parents=[parser_base])
        subparser.set_defaults(resource=name)
        module.Resource._add_arguments(parser_base, subparser)

    return parser.parse_args()


def main():
    args = parse_argv()
    if args.version:
        six.print_('lavaclient2 version ' + __version__)
        sys.exit(0)

    initialize_logging(args)
    execute_command(args)


if __name__ == '__main__':  # pragma: nocover
    main()
    sys.exit(0)
