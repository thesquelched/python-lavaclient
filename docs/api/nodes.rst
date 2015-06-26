Nodes
=====

.. automodule:: lavaclient.api.nodes

While most ways to interact with a cluster are available via the
:mod:`lavaclient.api.clusters` methods, you can interact with cluster nodes
directly using the :mod:`lavaclient.api.nodes` methods.  For example::

    >>> nodes = lava.nodes.list('fd8cbe7e-04e2-4329-b80e-26edb8fa39bb')
    >>> nodes
    [Node(id='58329654-09f5-45c2-86bc-a5469836c38d', name='master-1', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated),
     Node(id='7595cdb7-5cb9-4cde-b033-84709998a6e0', name='secondary-1', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated),
     Node(id='9831887a-88d6-4e35-9046-4c5ce0765b29', name='gateway-1', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated),
     Node(id='b32e94eb-ba88-43ef-a833-27824446b48e', name='slave-1', flavor_id, addresses, components, created, node_group, private_ip, public_ip, status, updated)]

    # Execute command over ssh
    >>> nodes[0].execute('scott', 'pwd',
    ...                  ssh_command='ssh -o StrictHostKeyChecking=no')
    '/home/scott'


API Reference
-------------

.. autoclass:: Resource()
   :members:

.. currentmodule:: lavaclient.api.response

.. autoclass:: Node()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: Addresses()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: Address()
   :members:
   :inherited-members:
   :member-order: groupwise
