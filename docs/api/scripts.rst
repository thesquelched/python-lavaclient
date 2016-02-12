Scripts
=======

.. automodule:: lavaclient.api.scripts

When booting up a cluster, you may want to run one or more custom scripts to do
further setup, e.g. creating users or installing additional packages.  While we
do not store your scripts on our servers, you can specify a URL from which your
scripts can be downloaded and executed directly on your cluster nodes.

.. note::

    Any script you associate with a cluster will be executed on *every* node.
    Therefore, if you have node-specific setup, you will have to build that
    logic directly into your script.

First, use the :meth:`~Resource.create` method to register your script with the
API::

    >>> script = lava.scripts.create(
            'create_users',
            'https://myhost.com/scripts/create_users.sh',
            'post_init')
    >>> script
    Script(id='5be7c29e-0df1-4e6f-be90-ada7dd0903f4', name='my_test_script', created, is_public, links, type, updated, url)

.. note::

    Currently, only post-init scripts are supported.  These run after the
    cluster setup is complete, including assigning IP's and installing stack
    services.

Then, you can associate the script with a new cluster and check the it's status
after the cluster finishes booting up::

    >>> cluster = lava.clusters.create(
            'script_cluster',
            'ALL_HDP2_2',
            ssh_keys=['my_key_name'],
            node_groups={'slave': {'count': 3, 'flavor': 'hadoop1-60'},
                         'zookeeper': {'count': 5}},
            user_scripts=[script.id],
            wait=True)
    >>> cluster.scripts
    [NodeScript(id='ef210ae9-7827-4c92-8caf-8c575033b89a', name='create_users', node_id, status)]

    >>> cluster.scripts[0].status
    'ACTIVE'

You may also :meth:`~Resource.update` your script if the need arises::

    >>> lava.scripts.update('5be7c29e-0df1-4e6f-be90-ada7dd0903f4',
                            url='http://newhostname.com/script.sh'))
    Script(id='5be7c29e-0df1-4e6f-be90-ada7dd0903f4', name='my_test_script', created, is_public, links, type, updated, url)

API Reference
-------------

.. autoclass:: Resource()
   :members:

.. currentmodule:: lavaclient.api.response

.. autoclass:: Script()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: NodeScript()
   :members:
   :inherited-members:
   :member-order: groupwise

   Returned from :attr:`ClusterDetail.scripts`
