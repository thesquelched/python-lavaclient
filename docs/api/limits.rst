Limits
======

.. automodule:: lavaclient.api.limits

Display aggregate resource limits for the tenant with which you authenticated.
For example::

    >>> limits = lava.limits.get()
    >>> limits
    AbsoluteLimits(disk, node_count, ram, vcpus)

    >>> limits.vcpus
    AbsoluteLimit(limit, remaining, used)

    >>> (limits.vcpus.used, limits.vcpus.remaining, limits.vcpus.limit)
    (12, 188, 200)


API Reference
-------------

.. autoclass:: Resource()
   :members:

.. currentmodule:: lavaclient.api.response

.. autoclass:: AbsoluteLimits()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: AbsoluteLimit()
   :members:
   :inherited-members:
   :member-order: groupwise
