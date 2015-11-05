Accessing Your Cluster
================================

Once you have a cluster, many of the tools in the ecosystem require command line access to your
cluster in order to run them.  ``ssh`` access is provided to all nodes in your cluster, apart from
the Ambari control node.  There is also the ability to set up a SOCKS proxy over ``ssh`` so you can
load internal cluster web pages in your browser.

Setting up your SSH credentials
-------------------------------

If you haven't defined any SSH credentials, when you create a cluster using ``lava``, it
will attempt to use your current username and SSH public key to provide access to your cluster::

    $ NODE_GROUPS='slave(flavor_id=hadoop1-7,count=3)'
    $ lava clusters create --node-groups $NODE_GROUPS my-cluster HADOOP_HDP2_3
    You have not uploaded any SSH key credentials; do you want to upload
    $HOME/.ssh/id_rsa.pub now?

If you want to specify a different SSH key, you can preload your SSH keys using the credentials
commands::

    $ lava credentials create_ssh_key my-ssh-key ~/.ssh/id_rsa.pub

Then you can specify your uploaded SSH key to be used for access to your cluster::

    $ lava clusters create --ssh-key my-ssh-key my-cluster HADOOP_HDP2_3

To specify a username that you want to be created on your clusters, you can pass that in the
cluster create call::

    $ lava clusters create --username my-username my-cluster HADOOP_HDP2_3

Once you have a cluster, you can SSH to it using the username that you supplied or your current
username if you left it at the default behavior::

    $ ssh my-username@<public-ip-of-node-in-cluster>

The IP addresses of your cluster nodes are visible by getting a list of nodes in your cluster::

    $ lava clusters nodes <cluster-id>


Shell Access via SSH
--------------------

``lava`` has a shortcut for getting SSH access to a node in your cluster.  By default, it will
pick a random node in your cluster. This saves you from having to look up the IP addresses::

    $ lava clusters ssh <cluster-id>
    Last login: Thu Jun 18 18:25:50 2015 from some.host
    [my-username@gateway-1 ~]$

If you want a specific host, you can use the node name to go to the host of your choice::

    $ lava clusters ssh --node-name master-1 <cluster-id>
    Last login: Thu Jun 18 18:25:50 2015 from some.host
    [my-username@master-1 ~]$

For most uses, if your stack has a ``gateway`` node, that is probably where you want to be, since
it has all of the cluster client libraries already installed and configured::

    $ lava clusters ssh --node-name gateway-1
    Last login: Thu Jun 18 18:25:50 2015 from some.host
    [my-username@gateway-1 ~]$

If you need custom ssh options, like you are using a different SSH keypair than the default, you
can supply a custom ``ssh`` command to be used::

    $ lava clusters ssh --ssh-command 'ssh -i ~/.ssh/id_rsa2 -o StrictHostKeyChecking=no'
    Last login: Thu Jun 18 18:25:50 2015 from some.host
    [my-username@gateway-1 ~]$


Web Page Access via SOCKS Proxy
-------------------------------

Many of the services in your cluster provide web pages to get status information about that
service.  Because these pages are not locked down with authenticated access, a firewall is
configured on your cluster to deny public access to them.  In order for you to access them, you
need to create a SOCKS proxy to a node in your cluster, at which point you can configure your web
browser to use this proxy and access the web pages as if you are within the cluster itself::

    $ lava clusters ssh_proxy <cluster_id>
    Starting SOCKS proxy via node gateway-1 (xxx.xxx.xxx.xxx)
    Successfully created SOCKS proxy on localhost:12345
    Use Ctrl-C to stop proxy

.. note::

    Make sure you configure your browser to use a SOCKS 5 proxy, not SOCKS 4. Each browser has a
    different method for configuring a proxy, so refer to your browser documentation if you don't
    know how to configure a proxy.

Until you hit Ctrl-C to kill the proxy, you can point your browser to use the proxy address
``localhost:12345``, at which point any page loads will be proxied through your cluster.

.. note::

    While the proxy is running, you probably want to avoid watching Netflix or Youtube, as
    that traffic will be proxied through your cluster and you will pay for the bandwidth used.  We
    suggest using a browser plugin that lets you easily turn proxies on and off so you only use it
    when you need to access your cluster.

All of your cluster nodes have an associated local hostname, so once you have the proxy running,
the local cluster DNS names like ``master-1.local`` will resolve for you as long as your browser is
configured to use the proxy.  This makes it possible  to load the pages using those hostnames in
your browser, such as ``http://master-1.local:50070`` for the ``HDFS NameNode`` web page.

.. note::

    You can also access the web pages using the private IP addresses of the nodes, but the
    hostnames are much more convenient and easier to remember.

To get a full list of available pages, query ``lava`` for your node information, which returns
any web page urls running on each node::

    $ lava clusters nodes <cluster-id>

Similar to the ``lava ssh`` command above, you can specify a custom ``ssh`` command to generate
your proxy::

    $ lava clusters ssh_proxy --ssh-command 'ssh -i ~/.ssh/id_rsa2'
    Starting SOCKS proxy via node gateway-1 (xxx.xxx.xxx.xxx)
    Successfully created SOCKS proxy on localhost:12345
    Use Ctrl-C to stop proxy

You can also override the default local port to use for running the proxy::

    $ lava clusters ssh_proxy <cluster_id> --port 15000
    Starting SOCKS proxy via node gateway-1 (xxx.xxx.xxx.xxx)
    Successfully created SOCKS proxy on localhost:15000
    Use Ctrl-C to stop proxy

You can also proxy through a specific node, rather than a random one::

    $ lava clusters ssh_proxy <cluster_id> --node-name master-1
    Starting SOCKS proxy via node master-1 (xxx.xxx.xxx.xxx)
    Successfully created SOCKS proxy on localhost:12345
    Use Ctrl-C to stop proxy
