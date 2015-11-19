import pytest
import shlex
import sys
from mock import patch, Mock, call
from figgis import Config, Field

from lavaclient.cli import parse_argv, print_unformatted_table


@patch('sys.argv', ['lava', 'authenticate', '--token', 'mytoken'])
def test_authenticate():
    args = parse_argv()
    assert args.token is None


@pytest.mark.parametrize('pre_args, post_args,key,value', [
    ('', '', 'verify_ssl', True),
    ('--insecure', '', 'verify_ssl', False),
    ('', '--insecure', 'verify_ssl', False),
    ('', '', 'endpoint', None),
    ('--endpoint foo/v2', '', 'endpoint', 'foo/v2'),
    ('', '--endpoint foo/v2', 'endpoint', 'foo/v2'),
])
def test_argparse_order(pre_args, post_args, key, value):
    argstr = 'lava {0} clusters list {1}'.format(pre_args, post_args)
    with patch('sys.argv', shlex.split(argstr)):
        args = parse_argv()

    assert getattr(args, key) == value


@patch('six.print_')
def test_print_unformatted(sixprint):
    class Conf(Config):
        table_columns = ('field1', 'field2')

        field1 = Field()
        field2 = Field()

    data = Conf(field1=1, field2=2)

    fake_args = Mock(delimiter=',', show_header=False)
    print_unformatted_table(fake_args, data)

    sixprint.assert_has_calls([
        call('field1,field2', file=sys.stderr),
        call('1,2'),
    ])
