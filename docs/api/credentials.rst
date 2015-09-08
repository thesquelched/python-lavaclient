Credentials
===========

.. currentmodule:: lavaclient.api.credentials

Manage cluster credentials, e.g. ssh keys, `Cloud Files
<http://www.rackspace.com/cloud/files>`_ account information.

When creating a cluster, you will need to provide a ssh key with which you can
log in to the cluster (since we do not generate passwords).  In the `lava`
script, if you have not created any ssh key credentials before creating a
cluster, you will be asked to create one using `$HOME/.ssh/id_rsa.pub`,
assuming that public key file exists.  However, when using
:class:`~lavaclient.Lava`, you will have to create your ssh credentials
manually::

    >>> ssh_key = lava.credentials.create_ssh_key('my_key',
    ...                                           '/path/to/id_rsa.pub')

    >>> lava.clusters.create(
    ...     'my_cluster',
    ...     'HADOOP_HDP2_2',
    ...     username='scott',
    ...     ssh_keys=[ssh_key.id],
    ...     node_groups={'slave': {'count': 3, 'flavor_id': 'hadoop1-7'}})

Similarly, you can add credentials to access other services from your clusters,
e.g. `Cloud Files <http://www.rackspace.com/cloud/files>`_, which you can
enable using the `credentials` argument when creating a cluster::

    >>> cloudfiles = lava.credentials.create_cloud_files('cloudfiles_user',
    ...                                                  'cloudfiles_apikey')

    >>> lava.clusters.create(
    ...     'my_cluster',
    ...     'HADOOP_HDP2_2',
    ...     username='scott',
    ...     ssh_keys=[ssh_key.id],
    ...     credentials=[{'cloud_files': cloudfiles.id}],
    ...     node_groups={'slave': {'count': 3, 'flavor_id': 'hadoop1-7'}})

.. note::

    The `connectors` argument has been replaced by `credentials`, which shares
    the same format.

.. note::

    You do not need to remember which attribute to use for each credential
    type; instead, you can always use the `id` attribute.  For example, when
    specifying ssh keys, you can use `ssh_key.id` instead of `ssh_key.name`.

.. note::

    The currently supported credential types are SSH, Cloud Files, Ambari, and
    Amazon S3.

API Reference
-------------

.. autoclass:: lavaclient.api.credentials.Resource()
   :members:

.. currentmodule:: lavaclient.api.response

.. autoclass:: Credentials()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: SSHKey()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: CloudFilesCredential()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: S3Credential()
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: AmbariCredential()
   :members:
   :inherited-members:
   :member-order: groupwise
