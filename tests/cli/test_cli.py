from mock import patch

from lavaclient.cli import parse_argv


@patch('sys.argv', ['lava', 'authenticate', '--token', 'mytoken'])
def test_authenticate():
    args = parse_argv()
    assert args.token is None
