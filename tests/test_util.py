import pytest
import six
from mock import patch
from figgis import Config, Field, ListField

from lavaclient import util


def test_b64encode():
    bindata = six.b('Zm9v')

    assert util.b64encode('foo') == bindata
    assert util.b64encode(six.u('foo')) == bindata
    assert util.b64encode(bindata) == bindata
    assert util.b64encode(six.b('foo')) == bindata


def test_getattrs():
    class Node(object):
        def __init__(self, value=None, left=None, right=None):
            self.value = value
            self.left = left
            self.right = right

    tree = Node(
        left=Node(1),
        right=Node(
            left=Node(2),
            right=Node(
                left=Node(3),
                right=Node(4)
            ),
        )
    )

    assert util.getattrs(tree, 'left.value') == 1
    assert util.getattrs(tree, 'right.left.value') == 2
    assert util.getattrs(tree, 'right.right.left.value') == 3
    assert util.getattrs(tree, 'right.right.right.value') == 4


def test_create_table():
    table = util.create_table([[1, 2], [3, 4]], ['foo', 'bar'])
    assert str(table) == """\
+-----+-----+
| foo | bar |
+-----+-----+
|   1 |   2 |
|   3 |   4 |
+-----+-----+"""


@pytest.mark.parametrize('data,header,title,output', [
    ([[1, 2], [3, 4]], ['foo', 'bar'], None, """\
+-----+-----+
| foo | bar |
+-----+-----+
|   1 |   2 |
|   3 |   4 |
+-----+-----+
"""),
    ([[1, 2], [3, 4]], ['foo', 'bar'], 'short', """\
+-----------+
|   short   |
+-----+-----+
| foo | bar |
+-----+-----+
|   1 |   2 |
|   3 |   4 |
+-----+-----+
"""),
    ([[1, 2], [3, 4]], ['foo', 'bar'], 'waytoofreakinglong', """\
+-----------------------+
|   waytoofreakinglong  |
+-----------+-----------+
|    foo    |    bar    |
+-----------+-----------+
|      1    |      2    |
|      3    |      4    |
+-----------+-----------+
"""),
])
def test_print_table(data, header, title, output):
    strio = six.StringIO()
    with patch('sys.stdout', strio):
        util.print_table(data, header, title=title)

    assert strio.getvalue() == output


@pytest.mark.parametrize('data,header,title,output', [
    ([1, 2], ['foo', 'bar'], None, """\
+-----+---+
| foo | 1 |
| bar | 2 |
+-----+---+
"""),
    ([1, 2], ['foo', 'bar'], 'short', """\
+---------+
|  short  |
+-----+---+
| foo | 1 |
| bar | 2 |
+-----+---+
"""),
    ([1, 2], ['foo', 'bar'], 'waytoofreakinglong', """\
+---------------------+
|  waytoofreakinglong |
+-----------+---------+
|    foo    |    1    |
|    bar    |    2    |
+-----------+---------+
"""),
])
def test_print_single_table(data, header, title, output):
    strio = six.StringIO()
    with patch('sys.stdout', strio):
        util.print_single_table(data, header, title=title)

    assert strio.getvalue() == output


def test_inject_client():
    class SubSubConf(Config):
        field = Field(int)

    class SubConf(Config):
        foo = Field(SubSubConf)
        bar = ListField(SubSubConf)
        baz = Field(int)

    class Conf(Config):
        one = Field(SubConf)
        two = ListField(SubConf)
        three = Field(int)

    client = object()
    subsubconf = dict(field=1)
    subconf = dict(foo=subsubconf, bar=[subsubconf, subsubconf], baz=1)
    conf = util.inject_client(
        client,
        Conf(one=subconf,
             two=[subconf, subconf],
             three=1))

    assert conf._client is client

    assert conf.one._client is client
    assert conf.one.foo._client is client
    assert all(item._client is client for item in conf.one.bar)

    assert all(item._client is client for item in conf.two)
    assert all(item.foo._client is client for item in conf.two)
    assert all(all(subitem._client is client for subitem in item.bar)
               for item in conf.two)
