Clusters
========

.. automodule:: lavaclient.api.clusters

You'll spend most of your time with :mod:`lavaclient` spinning up, tearing
down, and otherwise manipulating your clusters.

For example::

    >>> [key.name for key in lava.credentials.list_ssh_keys()]
    [u'scott@myhostname']

    >>> stack = lava.stacks.get('HADOOP_HDP2_2')
    >>> stack
    StackDetail(id='HADOOP_HDP2_2', name='Hadoop HDP 2.2', created, description, distro, links, node_groups, services)

    >>> stack.node_groups
    [StackNodeGroup(id='gateway', flavor_id, components, count, resource_limits),
     StackNodeGroup(id='master', flavor_id, components, count, resource_limits),
     StackNodeGroup(id='secondary', flavor_id, components, count, resource_limits),
     StackNodeGroup(id='slave', flavor_id, components, count, resource_limits)]

    >>> lava.flavors.list
    [Flavor(id='hadoop1-15', name='Medium Hadoop Instance', disk, links, ram, vcpus),
     Flavor(id='hadoop1-30', name='Large Hadoop Instance', disk, links, ram, vcpus),
     Flavor(id='hadoop1-60', name='XLarge Hadoop Instance', disk, links, ram, vcpus),
     Flavor(id='hadoop1-7', name='Small Hadoop Instance', disk, links, ram, vcpus)]

    >>> cluster = lava.clusters.create(
            'my_hadoop_cluster',
            'HADOOP_HDP2_2',
            username='scott',
            ssh_keys=['scott@myhostname'],
            node_groups=[{'id': 'slave', 'count': 1, 'flavor_id': 'hadoop1-7'}],
            wait=True)
    >>> cluster
    ClusterDetail(id='a12093dc-845b-4cfc-8b12-cec920695ccc', name='my_hadoop_cluster', stack_id, cbd_version, created, links, node_groups, progress, scripts, status, updated, username)

    # Look at cluster nodes
    [Node(id='58329654-09f5-45c2-86bc-a5469836c38d', name='master-1', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated),
     Node(id='7595cdb7-5cb9-4cde-b033-84709998a6e0', name='secondary-1', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated),
     Node(id='9831887a-88d6-4e35-9046-4c5ce0765b29', name='gateway-1', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated),
     Node(id='b32e94eb-ba88-43ef-a833-27824446b48e', name='slave-1', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated)]

    >>> slave = cluster.node_groups[-1]
    >>> slave.count
    1

    # Add two more slave nodes
    >>> cluster = cluster.resize(node_groups=[{'id': 'slave', 'count': 3}], wait=True)
    >>> [node for node in cluster.nodes if node.node_group == 'slave']
    [Node(id='b32e94eb-ba88-43ef-a833-27824446b48e', name='slave-1', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated),
     Node(id='26126a8e-cf2f-4e0a-a5b8-0d5c56f25036', name='slave-2', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated),
     Node(id='16e72fa1-7113-4020-81f6-de20a8c49b98', name='slave-3', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated)]

    # Execute command on gateway
    >>> cluster.ssh_execute_on_node('gateway-1', 'whoami')
    'scott\n'

    # Delete the cluster
    >>> cluster.delete()
    ClusterDetail(id='a12093dc-845b-4cfc-8b12-cec920695ccc', name='my_hadoop_cluster', stack_id, cbd_version, created, links, node_groups, progress, scripts, status, updated, username)


On the command line, you have a few additional useful commands available::

    $ lava clusters ssh a12093dc-845b-4cfc-8b12-cec920695ccc
    Last login: Thu Jun 18 18:25:50 2015 from some.host
    [scott@gateway-1 ~]$ exit
    logout
    Connection to xxx.xxx.xxx.xxx closed.

    $ lava clusters ssh_proxy a12093dc-845b-4cfc-8b12-cec920695ccc
    Starting SOCKS proxy via node gateway-1 (xxx.xxx.xxx.xxx)
    Successfully created SOCKS proxy on localhost:12345
    Use Ctrl-C to stop proxy
    ^CSOCKS proxy closed


API Reference
-------------

.. autoclass:: Resource()
   :members:

.. currentmodule:: lavaclient.api.response

.. autoclass:: Cluster()

   Only returned by :meth:`~lavaclient.api.clusters.Resource.list`. Has the
   same methods/attributes as :class:`~ClusterDetail` except for `node_group`,
   `progress`, and `scripts`


.. autoclass:: ClusterDetail()
   :members:
   :inherited-members:
   :member-order: groupwise


.. autoclass:: NodeGroup()
   :members:
   :inherited-members:
   :member-order: groupwise
