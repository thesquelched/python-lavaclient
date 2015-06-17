import pytest
from mock import patch, MagicMock

from lavaclient.client import Lava
from lavaclient.cli import initialize_logging


class Exits(Exception):
    pass


@pytest.fixture
def mock_client(request):
    client = Lava(
        'username',
        endpoint='http://dfw.bigdata.api.rackspacecloud.com/v2',
        token='token',
        tenant_id=12345)

    client._request = MagicMock()

    def init_logging(*args):
        initialize_logging(MagicMock(debug=True))

    def exit(*args):
        raise Exits(args)

    patchers = [
        patch('lavaclient.cli.initialize_logging', init_logging),
        patch('sys.exit', exit),
        patch('lavaclient.cli.create_client',
              MagicMock(return_value=client)),
    ]

    for patcher in patchers:
        patcher.start()
        request.addfinalizer(patcher.stop)

    return client


@pytest.fixture
def print_table(request):
    patcher = patch('lavaclient.util.print_table')
    request.addfinalizer(patcher.stop)
    return patcher.start()


@pytest.fixture
def print_single_table(request):
    patcher = patch('lavaclient.util.print_single_table')
    request.addfinalizer(patcher.stop)
    return patcher.start()


@pytest.fixture
def mock_stdout(request):
    patcher = patch('sys.stdout')
    request.addfinalizer(patcher.stop)
    return patcher.start()
