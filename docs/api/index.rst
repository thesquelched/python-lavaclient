API
===

.. currentmodule:: lavaclient

You can access the API methods directly from the :class:`Lava` client instance.
Each group of methods is named according to the plural form of the group, e.g.
`clusters` and `distros`, not `cluster` and `distro`.  For example::

    >>> client = Lava(...)
    
    # Cluster methods
    >>> clusters = client.clusters.list()
    >>> distros = client.distros.list()


Methods
-------

.. toctree::
   :maxdepth: 2
   :glob:

   *
