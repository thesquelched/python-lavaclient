Lava Client
===========

.. py:module:: lavaclient

.. currentmodule:: lavaclient

The :class:`Lava` client provides access to all public CloudBigData API
methods.


Authentication
--------------

Authenticating to the CloudBigData API is similar to that of any other
Rackspace product; you will need the following information:

- Rackspace username
- Tenant ID
- CloudBigData API key
- Region

You can get all of this information from the
`Rackspace Cloud Control Panel <https://mycloud.rackspace.com/>`_. The username
with which you log in is the same one you will need to authenticate using
:class:`Lava`.  To get the tenant ID, click on the `Account: <username>` link
in the upper-right; it will be at the top as `Account # <tenant>`.  The list of
available regions on the left; make sure to use the abbreviation, not the
proper name, e.g. `ORD` instead of `Chicago`.  Lastly, to find the API key,
click on the `Account: <username>` link again, and select `Account Settings`.
The API key will be under `Login Details`.

Now that you have the requisite information, you can create the client::

    >>> from lavaclient import Lava
    >>> client = Lava('myusername',
    ...               region='DFW',
    ...               api_key='807895ec1ec4ca255e49ccc6715bf29f',
    ...               tenant_id=123456)

Creating the client will cause it to automatically authenticate.  Each time you
authenticate, the client will receive a token, which you can use to prevent
having to authenticate again (until the token expires).  For example, you could
cache the token in a file, which you can re-use for future clients::

    >>> import os.path

    >>> TOKEN_CACHE = '/tmp/lava_token'

    >>> def make_client(username, region, api_key, tenant_id):
    ...     if os.path.isfile(TOKEN_CACHE):
    ...         with open(TOKEN_CACHE, 'r') as f:
    ...             token = f.read().strip()
    ...     else:
    ...         token = None
    ...
    ...     client = Lava(username,
    ...                   token=token,
    ...                   region=region,
    ...                   api_key=api_key,
    ...                   tenant_id=tenant_id)
    ...
    ...     with open(TOKEN_CACHE, 'w') as f:
    ...         f.write(client.token)
    ...
    ...     return client

The client will automatically reauthenticate during API calls if it detects
that the token has expired.  However, you can force the issue with
:meth:`~Lava.reauthenticate`.


API Reference
-------------

.. autoclass:: Lava
   :members:
   :member-order: groupwise

   .. attribute:: clusters

      See: :mod:`lavaclient.api.clusters`

   .. attribute:: limits

      See: :mod:`lavaclient.api.limits`

   .. attribute:: flavors

      See: :mod:`lavaclient.api.flavors`

   .. attribute:: stacks

      See: :mod:`lavaclient.api.stacks`

   .. attribute:: distros

      See: :mod:`lavaclient.api.distros`

   .. attribute:: workloads

      See: :mod:`lavaclient.api.workloads`

   .. attribute:: scripts

      See: :mod:`lavaclient.api.scripts`

   .. attribute:: nodes

      See: :mod:`lavaclient.api.nodes`

   .. attribute:: credentials

      See: :mod:`lavaclient.api.credentials`
