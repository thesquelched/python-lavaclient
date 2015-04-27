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

import math
import textwrap
import six
import binascii
import base64
import functools
from collections import namedtuple
from figgis import Config
from prettytable import PrettyTable


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
    return functools.reduce(getattr, path.split('.'), item)


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


Command = namedtuple('Command', ['arguments', 'function'])


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


def get_function_arguments(func):
    """Return (args, kwargs) for func, excluding `self`"""
    code = six.get_function_code(func)
    defaults = six.get_function_defaults(func) or []

    arg_names = [var for var in code.co_varnames[:code.co_argcount]
                 if var != 'self']
    n_required = len(arg_names) - len(defaults)

    return arg_names[:n_required], arg_names[n_required:]


def command(*args, **kwargs):
    """Decorator that creates an argparse subparser for the decorated
    function"""
    if args and (kwargs or not callable(args[0])):
        raise TypeError('command() takes zero or more keyword arguments')

    def decorator(func):
        required, optional = get_function_arguments(func)

        arguments = []

        # Add positional arguments
        for name in required:
            arg = kwargs.get(name, argument(name))
            if not arg.args or arg.args[0] != name:
                raise ValueError(
                    "Positional argument '{0}' must have the same name as "
                    "the function argument, '{1}'".format(arg.args[0], name))

            arg.kwargs.update(
                metavar=arg.kwargs.get('metavar', '<{0}>'.format(name)))

            arguments.append(arg)

        # Add optional arguments
        for i, name in enumerate(optional):
            if name not in kwargs:
                arg = argument('--' + name.replace('_', '-'),
                               metavar='<{0}>'.format(name))
            else:
                arg = kwargs[name]

            arg.kwargs.update(dest=name)
            arguments.append(arg)

        return Command(arguments=arguments, function=func)

    return decorator(args[0]) if args else decorator


class CommandLine(type):

    def __new__(cls, name, bases, dct):
        arguments = {}

        # Get list of items before modifying dct
        for key, value in list(dct.items()):
            if isinstance(value, Command):
                arguments[key] = value.arguments
                dct[key] = value.function

        @classmethod
        def add_arguments(cls, parser_base, parser, arguments=arguments,):
            subparsers = parser.add_subparsers()

            for cmd, args in arguments.items():
                subparser = subparsers.add_parser(cmd, parents=[parser_base])
                subparser.set_defaults(command=cmd)
                for arg in args:
                    arg.add_to_parser(subparser)

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
