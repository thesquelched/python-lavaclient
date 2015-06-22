Distributions
=============

.. automodule:: lavaclient.api.distros

All stacks are based on a distribution, which defines the available services,
their versions, and their components.

For example::

    >>> lava.distros.list()
    [Distro(id='HDP2.2', name='HortonWorks Data Platform', version)]

    >>> lava.distros.list()[0].to_dict()
    {'id': u'HDP2.2', 'name': u'HortonWorks Data Platform', 'version': u'2.2'}

    >>> hdp22 = lava.distro.get('HDP2.2')
    >>> hdp22
    DistroDetail(id='HDP2.2', name='HortonWorks Data Platform', services, version)

    >>> [service.name for service in hdp22.services]
    [u'HDFS', u'YARN', u'MapReduce', u'Hive', u'Pig', u'Sqoop', u'Oozie',
     u'Flume', u'Storm', u'Kafka', u'Zookeeper', u'Falcon', u'Spark']

    >>> hdp22.services[0].to_dict()
    {'components': [
        {u'name': u'Namenode'},
        {u'mode': u'Secondary', u'name': u'SecondaryNamenode'},
        {u'name': u'Datanode'}],
     'description': u'Hadoop Distributed File System (HDFS) is a scalable, fault-tolerant, distributed file system that provides scalable and reliable data storage designed to span large clusters of commodity servers.',
     'name': u'HDFS',
     'version': u'2.6.0'}


API Reference
-------------

.. autoclass:: Resource()
   :members:

.. currentmodule:: lavaclient.api.response

.. autoclass:: Distro()

   Only returned by :meth:`~lavaclient.api.distros.Resource.list`. Has the
   same methods/attributes as :class:`~DistroDetail` except for `services`


.. autoclass:: DistroDetail()
   :members:
   :inherited-members:
   :member-order: groupwise


.. autoclass:: DistroService()
   :members:
   :inherited-members:
   :member-order: groupwise
