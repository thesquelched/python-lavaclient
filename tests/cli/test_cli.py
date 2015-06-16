from mock import patch

from lavaclient2.cli import parse_argv


@patch('sys.argv', ['lava2', 'authenticate', '--token', 'mytoken'])
def test_authenticate():
    args = parse_argv()
    assert args.token is None
