from mock import patch, MagicMock
import pytest

from lavaclient2 import client


@pytest.fixture
def lavaclient():
    with patch.object(client.Lava, 'authenticate') as auth:
        auth.return_value = MagicMock(
            auth_token='auth_token',
            service_catalog=MagicMock(
                url_for=MagicMock(
                    return_value='endpoint'
                )
            )
        )
        return client.Lava('api_key',
                           'username',
                           'region',
                           auth_url='auth_url',
                           tenant_id='tenant_id',
                           verify_ssl=False)


@pytest.fixture
def link_response():
    return {
        'rel': 'rel',
        'href': 'href',
    }


@pytest.fixture
def flavor_response(link_response):
    return {
        'id': 'hadoop1-15',
        'name': 'Medium Hadoop Instance',
        'vcpus': 4,
        'ram': 15360,
        'disk': 2500,
        'links': [link_response],
    }


@pytest.fixture
def node_group():
    return {
        'id': 'node_id',
        'count': 1,
        'flavor_id': 'hadoop1-60',
        'components': {},
    }


@pytest.fixture
def distro_fixture():
    return {
        "id": "HDP2.2",
        "name": "HortonWorks Data Platform",
        "version": "2.2",
        "services": [
            {
                "components": [
                    {
                        "name": "Namenode"
                    },
                    {
                        "mode": "Secondary",
                        "name": "SecondaryNamenode"
                    },
                    {
                        "name": "Datanode"
                    },
                ],
                "modes": [
                    {
                        "name": "Secondary"
                    }
                ],
                "name": "HDFS",
                "version": "2.6",
                "description": (
                    "Hadoop Distributed File System (HDFS) is a scalable, "
                    "fault-tolerant, distributed file system that provides "
                    "scalable and reliable data storage designed to span "
                    "large clusters of commodity servers."
                )
            },
            {
                "components": [
                    {
                        "name": "ResourceManager"
                    },
                    {
                        "name": "NodeManager"
                    },
                    {
                        "name": "TimelineHistoryServer"
                    }
                ],
                "name": "Yarn",
                "version": "2.6",
                "description": (
                    "YARN (Yet Another Resource Negotiator) is a core "
                    "component of Hadoop, managing access to all resources "
                    "in a cluster. YARN brokers access to cluster compute "
                    "resources on behalf of multiple applications, using "
                    "selectable criteria such as fairness or capacity, "
                    "allowing for a more general-purpose resource management."
                )
            },
            {
                "components": [
                    {
                        "name": "MRHistoryServer"
                    },
                    {
                        "name": "MRClient"
                    }
                ],
                "name": "MapReduce",
                "version": "2.6",
                "description": (
                    "Hadoop MapReduce is a software framework for easily "
                    "writing applications which process vast amounts of data "
                    "(multi-terabyte data-sets) in-parallel on large clusters "
                    "of commodity hardware in a reliable, fault-tolerant "
                    "manner."
                )
            },
            {
                "components": [
                    {
                        "name": "HiveServer2"
                    },
                    {
                        "name": "HiveMetastore"
                    },
                    {
                        "name": "HiveAPI"
                    },
                    {
                        "name": "HiveClient"
                    }
                ],
                "name": "Hive",
                "version": "0.14.0",
                "description": (
                    "Apache Hive is a data warehouse infrastructure built on "
                    "top of Hadoop for providing data summarization, query, "
                    "and analysis. Hive provides a mechanism to project "
                    "structure onto this data and query the data using a "
                    "SQL-like language called HiveQL."
                )
            },
            {
                "components": [
                    {
                        "name": "PigClient"
                    }
                ],
                "name": "Pig",
                "version": "0.14.0",
                "description": (
                    "Apache Pig is a platform for analyzing large data sets "
                    "that consists of a high-level language (Pig Latin) for "
                    "expressing data analysis programs, coupled with "
                    "infrastructure for evaluating these programs. Pig Latin "
                    "abstracts the programming from the Java MapReduce idiom "
                    "into a notation similar to that of SQL for RDBMS systems."
                )
            }
        ]
    }
