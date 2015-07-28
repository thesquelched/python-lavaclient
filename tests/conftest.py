from mock import patch, MagicMock
import pytest

from lavaclient import client


@pytest.fixture
def lavaclient():
    with patch.object(client.Lava, '_authenticate') as auth:
        auth.return_value = MagicMock(
            auth_token='auth_token',
            service_catalog=MagicMock(
                url_for=MagicMock(
                    return_value='endpoint'
                )
            )
        )
        return client.Lava('username',
                           'region',
                           api_key='api_key',
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
def flavor(link_response):
    return {
        'id': 'hadoop1-15',
        'name': 'Medium Hadoop Instance',
        'vcpus': 4,
        'ram': 15360,
        'disk': 2500,
        'links': [link_response],
    }


@pytest.fixture
def flavors_response(flavor):
    return {'flavors': [flavor]}


@pytest.fixture
def node_group():
    return {
        'id': 'id',
        'count': 1,
        'flavor_id': 'hadoop1-60',
        'components': [{'name': 'component'}],
    }


@pytest.fixture
def distro(link_response):
    return {
        'id': 'HDP2.2',
        'links': [link_response],
        'name': 'HortonWorks Data Platform',
        'version': '2.2'
    }


@pytest.fixture
def distro_service():
    return {
        'components': [{'name': 'component'}],
        'description': 'description',
        'name': 'name',
        'version': 'version'
    }


@pytest.fixture
def distro_detail(distro, distro_service):
    data = distro.copy()
    data.update(services=[distro_service])
    return data


@pytest.fixture
def distros_response(distro):
    return {'distros': [distro]}


@pytest.fixture
def distro_response(distro_detail):
    return {'distro': distro_detail}


@pytest.fixture
def cluster_script():
    return {
        'id': 'script_id',
        'name': 'name',
        'status': 'status',
    }


@pytest.fixture
def cluster(link_response):
    return {
        'id': 'cluster_id',
        'created': '2014-01-01',
        'updated': None,
        'name': 'cluster_name',
        'status': 'ACTIVE',
        'stack_id': 'stack_id',
        'cbd_version': 1,
        'links': [link_response],
    }


@pytest.fixture
def cluster_detail(cluster, node_group, cluster_script):
    data = cluster.copy()
    data.update(
        node_groups=[node_group],
        username='username',
        scripts=[cluster_script],
        progress=1.0,
        credentials=[
            {'type': 'ssh_keys', 'name': 'mykey'},
            {'type': 'cloud_files', 'name': 'username'},
            {'type': 'ambari', 'name': 'username'},
            {'type': 's3', 'name': 'accesskey'},
        ],
    )
    return data


@pytest.fixture
def cluster_response(cluster_detail):
    return {'cluster': cluster_detail}


@pytest.fixture
def clusters_response(cluster):
    return {'clusters': [cluster]}


@pytest.fixture
def script(link_response):
    return {
        'id': 'id',
        'name': 'name',
        'type': 'POST_INIT',
        'url': 'url',
        'is_public': True,
        'created': '2015-01-01',
        'updated': '2015-01-01',
        'links': [link_response],
    }


@pytest.fixture
def scripts_response(script):
    return {'scripts': [script]}


@pytest.fixture
def script_response(script):
    return {'script': script}


@pytest.fixture
def absolute_limit():
    return {
        'limit': 10,
        'remaining': 0,
    }


@pytest.fixture
def absolute_limits(absolute_limit):
    return {
        'node_count': absolute_limit,
        'ram': absolute_limit,
        'disk': absolute_limit,
        'vcpus': absolute_limit,
    }


@pytest.fixture
def limit(absolute_limits, link_response):
    return {
        'absolute': absolute_limits,
        'links': [link_response]
    }


@pytest.fixture
def limits_response(limit):
    return {'limits': limit}


@pytest.fixture
def stack_service():
    return {
        'name': 'service_name',
        'modes': ['mode1'],
        'version': 'version',
        'components': [{'name': 'component'}],
    }


@pytest.fixture
def stack(stack_service, link_response):
    return {
        'id': 'stack_id',
        'name': 'stack_name',
        'distro': 'distro',
        'description': 'description',
        'services': [stack_service],
        'links': [link_response],
    }


@pytest.fixture
def stacks_response(stack):
    return {'stacks': [stack]}


@pytest.fixture
def stack_node_group():
    return {
        'id': 'id',
        'flavor_id': 'hadoop1-7',
        'count': 10,
        'components': [{'name': 'component'}],
        'resource_limits': {
            'min_count': 1,
            'max_count': 10,
            'min_ram': 1024,
        }
    }


@pytest.fixture
def stack_detail(stack, stack_node_group):
    data = stack.copy()
    data.update(
        created='2015-01-01',
        node_groups=[stack_node_group],
    )
    return data


@pytest.fixture
def stack_response(stack_detail):
    return {'stack': stack_detail}


@pytest.fixture
def workload():
    return {
        'id': 'id',
        'name': 'name',
        'caption': 'caption',
        'description': 'description',
    }


@pytest.fixture
def workloads_response(workload):
    return {'workloads': [workload]}


@pytest.fixture
def recommendation_size():
    return {
        'flavor': 'hadoop1-7',
        'minutes': 1.0,
        'nodecount': 2,
        'recommended': True,
    }


@pytest.fixture
def recommendation(recommendation_size):
    return {
        'name': 'name',
        'description': 'description',
        'requires': ['requires'],
        'sizes': [recommendation_size],
    }


@pytest.fixture
def recommendations_response(recommendation):
    return {'recommendations': [recommendation]}


@pytest.fixture
def node(link_response):
    return {
        'id': 'node_id',
        'name': 'NODENAME',
        'status': 'ACTIVE',
        'created': '2014-01-01',
        'updated': None,
        'flavor_id': 'flavor_id',
        'node_group': [],
        'addresses': {
            'public': [
                {
                    'addr': '1.2.3.4',
                    'version': '4.0'
                }
            ],
            'private': [
                {
                    'addr': '5.6.7.8',
                    'version': '4.0'
                }
            ]
        },
        'components': [
            {
                'name': 'component_name',
                'nice_name': 'Component name',
                'uri': 'http://host'
            }
        ],
        "links": [link_response]
    }


@pytest.fixture
def nodes_response(node):
    return {'nodes': [node]}


@pytest.fixture
def ssh_key():
    return {'key_name': 'mykey', 'public_key': 'a' * 50}


@pytest.fixture
def cloud_files():
    return {'username': 'username', 'api_key': 'a' * 25}


@pytest.fixture
def s3():
    return {'access_key_id': 'access_key_id', 'access_secret_key': 'a' * 40}


@pytest.fixture
def ambari():
    return {'username': 'username', 'password': 'password'}


@pytest.fixture
def ssh_key_response(ssh_key):
    return {'credentials': {'ssh_keys': ssh_key}}


@pytest.fixture
def ssh_keys_response(ssh_key):
    return {'credentials': {'ssh_keys': [ssh_key]}}


@pytest.fixture
def cloud_files_cred_response(cloud_files):
    return {'credentials': {'cloud_files': cloud_files}}


@pytest.fixture
def cloud_files_creds_response(cloud_files):
    return {'credentials': {'cloud_files': [cloud_files]}}


@pytest.fixture
def s3_cred_response(s3):
    return {'credentials': {'s3': s3}}


@pytest.fixture
def s3_creds_response(s3):
    return {'credentials': {'s3': [s3]}}


@pytest.fixture
def ambari_cred_response(ambari):
    return {'credentials': {'ambari': ambari}}


@pytest.fixture
def ambari_creds_response(ambari):
    return {'credentials': {'ambari': [ambari]}}


@pytest.fixture
def credentials_response(ssh_key, cloud_files, s3, ambari):
    return {
        'credentials': {
            'ssh_keys': [ssh_key],
            'cloud_files': [cloud_files],
            's3': [s3],
            'ambari': [ambari],
        }
    }
