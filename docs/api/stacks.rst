Stacks
======

.. automodule:: lavaclient.api.stacks

A stack describes the layout of a cluster, including flavor and number of nodes
and what services should be installed, e.g. HDFS, Storm, Spark, etc.  The Cloud
Big Data provides a number of pre-defined stacks on which you may base your
clusters.  To see a list of stacks, use the :meth:`~Resource.list` method::

    >>> stacks = lava.stacks.list()
    >>> stacks
    [Stack(id='ALL_HDP2_2', name='HDP 2.2 with all services', description, distro, links, services),
     Stack(id='HADOOP_HDP2_2', name='Hadoop HDP 2.2', description, distro, links, services),
     Stack(id='HDP2_2_SANDBOX', name='Hadoop HDP 2.2 All-in-One Sandbox', description, distro, links, services),
     Stack(id='KAFKA_HDP2_2', name='Kafka on HDP 2.2', description, distro, links, services),
     Stack(id='STORM_HDP2_2', name='Real-time processing on HDP 2.2 with Storm/Kafka', description, distro, links, services)]

    >>> all_hdp2_2 = stacks[0]
    >>> all_hdp2_2.distro
    'HDP2.2'

    >>> all_hdp2_2.services
    [StackService(name='Flume', modes),
     StackService(name='HDFS', modes),
     StackService(name='Zookeeper', modes),
     StackService(name='Sqoop', modes),
     StackService(name='MapReduce', modes),
     StackService(name='Hive', modes),
     StackService(name='Pig', modes),
     StackService(name='YARN', modes),
     StackService(name='Storm', modes),
     StackService(name='Oozie', modes),
     StackService(name='Falcon', modes),
     StackService(name='Kafka', modes)]

If you want to get more detail on a stack, either use the :meth:`~Resource.get`
method, or call :meth:`~lavaclient.api.response.Stack.refresh` method on the
stack object::

    >>> all_hdp2_2 = all_hdp2_2.refresh()
    >>> all_hdp2_2
    StackDetail(id='ALL_HDP2_2', name='HDP 2.2 with all services', created, description, distro, links, node_groups, services)

    >>> all_hdp2_2.node_groups
    [StackNodeGroup(id='gateway', flavor_id, components, count, resource_limits),
     StackNodeGroup(id='master', flavor_id, components, count, resource_limits),
     StackNodeGroup(id='secondary', flavor_id, components, count, resource_limits),
     StackNodeGroup(id='service-master', flavor_id, components, count, resource_limits),
     StackNodeGroup(id='slave', flavor_id, components, count, resource_limits),
     StackNodeGroup(id='zookeeper', flavor_id, components, count, resource_limits)]

    >>> all_hdp2_2.node_groups[0].components
    [{'name': 'HiveServer2'},
     {'name': 'HiveMetastore'},
     {'name': 'HiveAPI'},
     {'name': 'HiveClient'},
     {'name': 'PigClient'},
     {'name': 'MRClient'},
     {'name': 'SqoopClient'},
     {'name': 'OozieClient'},
     {'name': 'FlumeHandler'},
     {'name': 'ZookeeperClient'},
     {'name': 'FalconClient'}]

.. note::

    In the future, you will be able to create and delete your own custom
    stacks.

API Reference
-------------

.. autoclass:: Resource()
   :members:

.. currentmodule:: lavaclient.api.response

.. autoclass:: Stack()
    
    Same as :class:`StackDetail`, except missing `created` and `node_groups`
    attributes

.. autoclass:: StackDetail()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: StackService()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: StackNodeGroup()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: ResourceLimits()
   :members:
   :inherited-members:
   :member-order: groupwise
