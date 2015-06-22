Introduction
============

:mod:`lavaclient` provides python bindings for the Rackspace CloudBigData API,
as well as a command-line client, which allows you to quickly and easily manage
your clusters.


Supernova
---------

The `lava` command-line client can be a bit verbose at times, due to the number
of arguments required for proper authentication.  For example, listing clusters
might look like this::

    $ lava --tenant 123456 --region dfw --user thisismyuser --api-key 807895ec1ec4ca255e49ccc6715bf29f clusters list

To save yourself a lot of time and keystrokes, you can instead set environment
variables to automatically inject this information to your `lava` calls::

    $ cat ~/.bashrc
    export LAVA_TENANT_NAME=123456
    export LAVA_REGION_NAME=dfw
    export LAVA_USERNAME=thisismyuser
    export LAVA_API_KEY=807895ec1ec4ca255e49ccc6715bf29f 

    $ lava clusters list

Unfortunately, this does not help very much when switching between regions or
other settings.  However, you can use
`supernova <http://supernova.readthedocs.org/en/latest/>`_ to help manage these
settings.  First, install `supernova`::

    $ pip install git+https://github.com/major/supernova.git#egg=supernova

.. warning::

    The version of `supernova` in pypi is broken and should not be used.
    Instead, install directly from the git repo.

Then, create a `.supernova` file in your home directory.  This uses the
`standard python configuration file format
<https://docs.python.org/2/library/configparser.html#module-ConfigParser>`_,
with one or more sections corresponding to different environments.  For
example, this `.supernova` file defines two environments, `dev` and `prod`, in
the `DFW` and `IAD` regions, respectively::

    [dev]
    LAVA_TENANT_NAME=123456
    LAVA_REGION_NAME=dfw
    LAVA_USERNAME=thisismyuser
    LAVA_API_KEY=807895ec1ec4ca255e49ccc6715bf29f 

    [prod]
    LAVA_TENANT_NAME=123456
    LAVA_REGION_NAME=iad
    LAVA_USERNAME=thisismyuser
    LAVA_API_KEY=807895ec1ec4ca255e49ccc6715bf29f 

You can then use `supernova` to list all of the cluters in your `dev`
environment::

    $ supernova -x lava dev clusters list
