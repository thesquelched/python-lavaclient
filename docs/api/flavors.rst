Flavors
=======

.. automodule:: lavaclient.api.flavors

Get information about the various node flavors available, which is important
when creating clusters and understanding stacks.  For example, the
`HADOOP_HDP2_2` stack has four node groups, one of which is the `slave` node
group.  When creating a cluster with this stack, you will need to choose the
number of slave nodes to create, as well as their flavor (that is, how much
memory and disk space and how many CPU's are available).

You may use the :meth:`~lavaclient.api.flavors.Resource.list` method to view
all available flavors in a region::

    >>> flavors = lava.flavors.list()
    >>> flavors
    [Flavor(id='hadoop1-15', name='Medium Hadoop Instance', disk, links, ram, vcpus),
     Flavor(id='hadoop1-30', name='Large Hadoop Instance', disk, links, ram, vcpus),
     Flavor(id='hadoop1-60', name='XLarge Hadoop Instance', disk, links, ram, vcpus),
     Flavor(id='hadoop1-7', name='Small Hadoop Instance', disk, links, ram, vcpus)]

    >>> for flavor in sorted(flavors, key=lambda flavor: flavor.vcpus):
    ...     print(flavor.id, flavor.vcpus, flavor.ram, flavor.disk)
    hadoop1-7 2 7680 1250
    hadoop1-15 4 15360 2500
    hadoop1-30 8 30720 5000
    hadoop1-60 16 61440 10000

API Reference
-------------

.. autoclass:: Resource()
   :members:

.. currentmodule:: lavaclient.api.response

.. autoclass:: Flavor()
   :members:
   :inherited-members:
   :member-order: groupwise
