# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Utility functions
"""

import shlex
import subprocess
import logging
import time
import json
import argparse
import math
import textwrap
import six
import binascii
import base64
import os.path
import six.moves.urllib as urllib
import socks
import warnings
from sockshandler import SocksiPyHandler
from functools import wraps
from collections import namedtuple
from figgis import Config
from prettytable import PrettyTable

from lavaclient.log import NullHandler
from lavaclient import error


RETRY_DEFAULT_ATTEMPTS = 3
RETRY_DEFAULT_DELAY = 1
RETRY_DEFAULT_BACKOFF = 2


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


def retry(*args, **kwargs):
    """Retry decorator"""
    attempts = max(kwargs.get('attempts', RETRY_DEFAULT_ATTEMPTS), 1)
    delay = max(kwargs.get('delay', RETRY_DEFAULT_DELAY), 0)
    backoff = max(kwargs.get('backoff', RETRY_DEFAULT_BACKOFF), 0)

    exceptions = kwargs.get('exceptions')
    if exceptions is None:
        exceptions = (Exception,)
    elif isinstance(exceptions, Exception):
        exceptions = (exceptions,)
    else:
        exceptions = tuple(exceptions)

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            delay_time = delay

            for attempt in six.moves.range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    LOG.debug('Attempt %d failed', attempt, exc_info=exc)
                    if attempt == attempts:
                        raise

                    time.sleep(delay_time)
                    delay_time *= backoff

            assert False, "This should never ever happen"

        return wrapped
    return decorator(args[0]) if args and callable(args[0]) else decorator


def expand(path):
    """Fully expand OS path"""
    return os.path.expanduser(os.path.expandvars(path))


def strip_url(url):
    """Ensure that the API endpoint URL does not end with a slash"""
    return url.rstrip('/')


def b64encode(value):
    try:
        base64.b64decode(value)
        return value
    except (binascii.Error, TypeError):
        if isinstance(value, six.binary_type):
            encoded = value
        else:
            encoded = value.encode('utf8')

        return base64.b64encode(encoded)


def create_table(data, header):
    table = PrettyTable(header)
    types = [set() for i in range(len(header))]

    for row in data:
        for i, item in enumerate(row):
            types[i].add(type(item))

        table.add_row(row)

    for name, name_types in zip(header, types):
        if name_types.issubset(set([float, int])):
            table.align[name] = 'r'
            table.float_format[name] = '.2'

    return table


def create_single_table(data, header):
    table = PrettyTable(header=False)

    table.add_column('Property', header, align='l')
    table.add_column('Value', data, align='r')

    table.float_format['Value'] = '.2'

    return table


def print_titled(table, title=None):
    if title:
        width = len(str(table).split('\n', 1)[0])
        if width < len(title) + 4:
            n_fields = len(table.field_names)
            padding = table.padding_width

            # Add padding to cover the space needed so that the table is as
            # wide as the title
            table.padding_width += int(math.ceil(
                (len(title) + 4 - width) /
                (2.0 * n_fields)))

            extra_width = 2 * n_fields * (table.padding_width - padding)
            width += extra_width

        six.print_('+' + '-' * (width - 2) + '+')
        six.print_('| ' + title.center(width - 4) + ' |')

    six.print_(table)


def print_table(data, header, title=None):
    """
    Print a pretty table from multiple rows
    """
    print_titled(create_table(data, header), title)


def print_single_table(data, header, title=None):
    """
    Print a pretty table for a single item
    """
    print_titled(create_single_table(data, header), title)


def no_nulls(data):
    return ['' if item is None else item for item in data]


def getattrs(item, path):
    """Like getattr, but works will paths, e.g. 'foo.bar', which will return
    item.foo.bar"""
    return six.moves.reduce(getattr, path.split('.'), item)


def table_attributes(response_class):
    """Return a tuple of response_class attributes that can be used to display
    a table"""
    attr_order = ('id', 'name', 'status')
    fields = response_class._fields

    attributes = [attr for attr in attr_order if attr in fields]
    attributes.extend(attr for attr in fields if attr not in set(attr_order))

    return attributes


def table_header(attributes):
    """Return a reasonable guess at a nice-looking set of attribute headers"""
    # Hard-coded attribute-to-header mapping
    header_map = {
        'id': 'ID',
    }
    return [header_map.get(attr, attr.capitalize().replace('_', ' '))
            for attr in attributes]


def table_data(response, response_class):
    """Transform API response into (table data, table header)"""
    attributes = getattr(response_class, 'table_columns',
                         table_attributes(response_class))
    header = getattr(response_class, 'table_header',
                     table_header(attributes))

    if not isinstance(response, list):
        data = no_nulls(getattrs(response, attr) for attr in attributes)
    else:
        data = (
            no_nulls(getattrs(item, column) for column in attributes)
            for item in response
        )

    return data, header or attributes


def display_result(result, response_config, title=None):
    """Pretty-print an instance (or list of instances) of response_config"""

    data, header = table_data(result, response_config)
    if not isinstance(result, list):
        print_single_table(data, header, title=title)
    else:
        print_table(data, header, title=title)


def display_table(response_config, title=None):
    """
    In the CLI interface, display the result of the decorated method as a
    table.  response_config should be the response (i.e. figgis.Config) class
    returned by the decorated method
    """
    if not issubclass(response_config, Config):
        raise TypeError('Response class class must be a figgis.Config')

    def wrapper(func):
        def display_func(*args, **kwargs):
            result = func(*args, **kwargs)

            if hasattr(response_config, 'display'):
                if isinstance(result, (list, tuple)):
                    for item in result:
                        response_config.display(result)
                else:
                    response_config.display(result)

                return

            display_result(result, response_config, title=title)

        func.display = display_func
        return func
    return wrapper


def display(display_function):
    """
    Attach a display function to the API method.  display_function should be a
    function that takes the response from the decorated method
    """
    def wrapper(func):
        def display_func(*args, **kwargs):
            return display_function(func(*args, **kwargs))

        func.display = display_func
        return func

    return wrapper


def percentage(number, total):
    """Return number as percentage of total"""
    return 0.0 if number == 0 else 100.0 * number / total


def post_binary(value):
    """Return binary data formatted property for POST data"""
    if isinstance(value, six.binary_type):
        return value.decode('utf8')
    return six.text_type(value)


Command = namedtuple('Command', ['arguments', 'function', 'parser_options'])


class argument(object):

    """Represents arguments to add to an argparse.ArgumentParser"""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, parser):
        parser.add_argument(*self.args, **self.kwargs)

    def __repr__(self):
        return 'ParserArgs(args={0}, kwargs={1})'.format(
            self.args, self.kwargs)


class mutually_exclusive(object):

    """Represents mutually exclusive optional arguments"""

    def __init__(self, arguments):
        self.arguments = arguments

    def add_to_parser(self, parser):
        group = parser.add_mutually_exclusive_group()
        for arg in self.arguments:
            group.add_argument(*arg.args, **arg.kwargs)


def get_function_arguments(func):
    """Return (args, kwargs) for func, excluding `self`"""
    code = six.get_function_code(func)
    defaults = six.get_function_defaults(func) or []

    arg_names = [var for var in code.co_varnames[:code.co_argcount]
                 if var != 'self']
    n_required = len(arg_names) - len(defaults)

    return arg_names[:n_required], arg_names[n_required:]


def _required_argument(name, arg):
    """Process a required argument"""
    if arg.args and arg.args[0] != name:
        raise ValueError(
            "Positional argument '{0}' must have the same name as "
            "the function argument, '{1}'".format(arg.args[0], name))
    elif not arg.args:
        arg.args = (name,)

    arg.kwargs.update(
        metavar=arg.kwargs.get('metavar', '<{0}>'.format(name)))

    return arg


def _optional_argument(name, arg):
    """Process an optional argument"""
    # Automatically inject option string
    if not arg.args:
        arg.args = ('--' + name.replace('_', '-'),)

    arg.kwargs.update(dest=name)

    return arg


def _default_optional_argument(varname):
    """Return the default argparse options for a function variable"""
    return argument('--' + varname.replace('_', '-'),
                    metavar='<{0}>'.format(varname))


def command(*args, **kwargs):
    """
    command(parser_help=None, **arguments)

    Decorator that creates an argparse subparser for the decorated function.
    Each argument key should be the name of n argument in the decorator
    function, while the argument value should be a call to the `argument`
    function, which acts as a pass-through to argparse's `add_argument`
    function.  Note that you do not have to specify the name in the call to
    `argument`, as it will be automatically injected.

    Positional function arguments should be positional argparse arguments as
    well, and likewise with keyword arguments and argparse optional arguments.
    Any arguments not included will be automatically added with no help text.

    Note that the `dest` option to `add_argument` will always be overridden so
    that it properly matches the decorated fuction argument names.

    :param parser_help: An optional help string to be passed to the subparser
                        that contains the argument for the decorated function

    Examples:

    >>> from lavaclient.api.resource import Resource

    >>> class MyResource(Resource):
    ...
    ...     @command(parser_options={
    ...                 'help': 'Get the thing',
    ...                 'epilog': 'Some additional help text at the end'},
    ...              thing_id=argument(type=int, help='The ID for the thing'),
    ...              an_option=argument('--my-option', '-m'))
    ...     def get_thing(self, thing_id, an_option=None):
    ...         # do some stuff
    ...         pass
    ...
    ...     @command
    ...     def do_something(self, name, value, some_option=None):
    ...         # Automatically inject all options
    ...         pass
    """
    FORBIDDEN_KEYS = frozenset(['parents', 'formatter_class'])

    if args and (kwargs or not callable(args[0])):
        raise TypeError('command() takes zero or more keyword arguments')

    parser_options = kwargs.pop('parser_options', {})
    if not isinstance(parser_options, dict):
        raise TypeError('parser_options must be a dictionary of arguments to '
                        'pass in during subparser creation')

    if frozenset(parser_options.keys()).intersection(FORBIDDEN_KEYS):
        raise TypeError('You may not include the following keys in '
                        'parser_options: {0}'.format(
                            ', '.join(FORBIDDEN_KEYS)))

    def decorator(func, parser_options=parser_options):
        required, optional = get_function_arguments(func)

        arguments = []

        # Add positional arguments
        for name in required:
            arg = kwargs.get(name, argument(name))
            arguments.append(_required_argument(name, arg))

        # Add optional arguments
        for name in optional:
            arg = kwargs.get(name, _default_optional_argument(name))

            if isinstance(arg, mutually_exclusive):
                argument.append(mutually_exclusive([
                    _optional_argument(name, item)
                    for item in arg.arguments]))
            else:
                arguments.append(_optional_argument(name, arg))

        return Command(arguments=arguments,
                       parser_options=parser_options,
                       function=func)

    return decorator(args[0]) if args else decorator


class CommandLine(type):

    def __new__(cls, name, bases, dct):
        arguments = {}
        parser_options = {}

        # Get list of items before modifying dct
        for key, value in list(dct.items()):
            if isinstance(value, Command):
                arguments[key] = value.arguments
                parser_options[key] = value.parser_options
                dct[key] = value.function

        @classmethod
        def add_arguments(cls, parser_base, parser, arguments=arguments,
                          parser_options=parser_options):
            subparsers = parser.add_subparsers()

            for cmd, args in arguments.items():
                parser_opts = parser_options.get(cmd, {})
                subparser = subparsers.add_parser(
                    cmd.strip('_'), parents=[parser_base],
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    **parser_opts)
                subparser.set_defaults(method=cmd)
                group = subparser.add_argument_group('Command Arguments')
                for arg in args:
                    arg.add_to_parser(group)

        dct['_add_arguments'] = add_arguments

        return type.__new__(cls, name, bases, dct)


def pretty_dict(data):
    keypairs = ('{0}={1}'.format(key, _prettify(value))
                for key, value in data.items())
    return '\n'.join(textwrap.wrap('{' + ', '.join(keypairs) + '}', 30))


def _prettify(data):
    if isinstance(data, (list, tuple)):
        if any(isinstance(item, Config) for item in data):
            datastr = ',\n'.join(pretty_dict(item.to_dict())
                                 for item in data)
        elif any(isinstance(item, dict) for item in data):
            datastr = ',\n'.join(pretty_dict(item)
                                 for item in data)
        else:
            datastr = ',\n'.join(data)

        return '[{0}]'.format(datastr)
    elif isinstance(data, dict):
        return pretty_dict(data)
    elif isinstance(data, Config):
        return pretty_dict(data.to_dict())
    else:
        return six.text_type(data)


def prettify(*fields):
    """Class decorator that adds a property '_<field>' for each field that
    yields a prettified version of the value, assuming the field type is
    either dict or a subclass of figgis.Config"""

    def decorator(cls):

        for field in fields:
            if field not in cls._fields:
                raise TypeError('Cannot prettify unknown field: {0}'.format(
                    field))

            def prettifier(self, field=field):
                return _prettify(getattr(self, field))

            setattr(cls, '_' + field, property(prettifier))

        return cls
    return decorator


def first_exists(*args):
    """
    first_exists(*args)

    Return the first argument that evaluates to True; equivalent to
    chaining the arguments together with `or`"""
    if not args:
        raise ValueError('Requires one or more arguments')

    return next((item for item in args if item),
                args[-1])


def file_or_string(value):
    """Either read file contents or return the string value"""
    try:
        with open(expand(value)) as handle:
            return handle.read()
    except IOError:
        return value


def read_json(value):
    """Either parse a raw JSON string or read JSON data from a file"""
    data = file_or_string(value)
    return json.loads(data)


def coroutine(func):
    """Decorator that simplifies making a coroutine"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        coro = func(*args, **kwargs)
        coro.send(None)
        return coro
    return wrapper


@retry(attempts=5,
       exceptions=[socks.ProxyConnectionError, socks.GeneralProxyError])
def test_socks_connection(url, proxy_host, proxy_port):
    """Return HTTP code from opening URL via SOCKS proxy"""
    opener = urllib.request.build_opener(
        SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, proxy_host, proxy_port))
    resp = opener.open(url)
    try:
        return resp.code
    finally:
        resp.close()


def create_socks_proxy(username, host, port, ssh_command=None, test_url=None):
    """Create a SOCKS proxy via SSH"""
    if isinstance(ssh_command, six.string_types):
        ssh_command = shlex.split(ssh_command)
    elif ssh_command is None:
        ssh_command = ['ssh']

    options = [
        '-o', 'PasswordAuthentication=no', '-o', 'BatchMode=yes', '-N',
        '-D', str(port)]
    command = ssh_command + options + ['{0}@{1}'.format(username, host)]

    LOG.debug('SSH proxy command: %s', ' '.join(command))
    process = subprocess.Popen(
        [expand(item) for item in command],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE)

    if not test_url:
        if process.poll():
            output, _ = process.communicate()
            LOG.critical('SOCKS proxy failed: %s', output)
            raise error.LavaError('Failed to set up SOCKS proxy')

        LOG.warn("No test URI's found; proxy may not be established yet")
        return process

    if process.poll():
        output, _ = process.communicate()
        LOG.critical('SOCKS proxy failed: %s', output)
        raise error.LavaError('Failed to set up SOCKS proxy')

    try:
        code = test_socks_connection(test_url, '127.0.0.1', port)
        if code >= 400:
            LOG.debug('Connection to %s through SOCKS proxy failed '
                      'with HTTP code %d', test_url, code)
            raise error.ProxyError('SOCKS proxy connection failed')

        return process
    except socks.ProxyConnectionError as exc:
        process.kill()
        LOG.critical('Failed to establish SOCKS proxy', exc_info=exc)
        six.raise_from(error.ProxyError('Failed to establish SOCKS proxy'),
                       exc)
    except Exception:
        process.kill()
        raise


def create_ssh_tunnel(username, node, local_port, remote_port,
                      ssh_command=None):
    """Create SSH tunnel on localhost:local_port to host:remote_port"""
    if isinstance(ssh_command, six.string_types):
        ssh_command = shlex.split(ssh_command)
    elif ssh_command is None:
        ssh_command = ['ssh']

    options = [
        '-o', 'PasswordAuthentication=no', '-o', 'BatchMode=yes', '-N',
        '-L', ':'.join([str(local_port), node.name, str(remote_port)])]
    command = ssh_command + options + ['@'.join([username, node.public_ip])]

    LOG.debug('SSH tunnel command: %s', ' '.join(command))
    process = subprocess.Popen(
        [expand(item) for item in command],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE)

    if process.poll():
        output, _ = process.communicate()
        LOG.critical('SSH tunnel failed: %s', output)
        raise error.LavaError('Failed to set up SSH tunnel')

    return process


def inject_client(client, obj):
    """Inject the `_client` attribute into every figgis.Config nested in the
    object"""
    if isinstance(obj, Config):
        obj._client = client
        inject_client(client, list(obj._properties.values()))
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            inject_client(client, item)
    elif isinstance(obj, dict):
        for item in obj.values():
            inject_client(client, item)

    return obj


def ssh_to_host(username, host, ssh_command=None, command=None):
    """SSH to a host"""
    if isinstance(ssh_command, six.string_types):
        ssh_cmd = shlex.split(ssh_command)
    elif isinstance(ssh_command, (list, tuple)):
        ssh_cmd = list(ssh_command)
    elif ssh_command is None:
        ssh_cmd = ['ssh']
    else:
        ssh_cmd = ssh_command

    command_list = ssh_cmd + ['{0}@{1}'.format(username, host)]
    if command:
        command_list.append(six.text_type(command))

    LOG.debug('SSH command: %s', ' '.join(command_list))

    if command:
        proc = subprocess.Popen(
            [expand(item) for item in command_list],
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE)

        output = proc.communicate()[0]
        returncode = proc.returncode
    else:
        returncode = subprocess.call([expand(item) for item in command_list])
        output = None

    if returncode:
        msg = 'Command returned non-zero status code {0}'.format(
            proc.returncode)
        LOG.error(msg)
        LOG.debug('Command output:\n%s', output)

        raise error.FailedError(msg)

    return output


def confirm(message, default_yes=False):
    """Present the user with a y/n choice. Returns True if the choice is `y`"""
    choices = 'Y/n' if default_yes else 'y/N'

    while True:
        resp = six.moves.input('{0} [{1}] '.format(message, choices)).lower()

        if not resp:
            resp = 'y' if default_yes else 'n'

        if resp in ('y', 'n'):
            break

        six.print_('Invalid selection: {0}'.format(resp))

    return resp == 'y'


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)
