import pytest
import shlex
from mock import patch

from lavaclient.cli import parse_argv


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
