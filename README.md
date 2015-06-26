python-lavaclient
=================

An API client for the Rackspace Cloud Big Data API

## Install

Install from `pip`

```console
$ pip install lavaclient
```

## Usage

For a list of commands
```console
$ lava --help

usage: lava [-h] [--token TOKEN] [--api-key LAVA_API_KEY] [--region REGION]
             [--tenant TENANT] [--version VERSION] [--debug]
             [--endpoint ENDPOINT] [--auth-url AUTH_URL] [--headless]
             [--user USER] [--password PASSWORD] [--insecure]
             
             {flavors,shell,limits,credentials,authenticate,scripts,clusters,nodes,workloads,stacks,distros}
             ...
             
optional arguments:
  -h, --help            show this help message and exit
  
General Options:
  --token TOKEN         Lava API authentication token
  --api-key LAVA_API_KEY
                        Lava API key
  --region REGION       API region, e.g. DFW
  --tenant TENANT       Tenant ID
  --version VERSION     Print client version
  --debug, -d           Print debugging information
  --endpoint ENDPOINT   API endpoint URL
  --auth-url AUTH_URL   Keystone endpoint URL
  --headless            Do not request user input
  --user USER           Keystone auth username
  --password PASSWORD   Keystone auth password
  --insecure, -k        Turn of SSL cert validation
  
Commands:
  {flavors,shell,limits,credentials,authenticate,scripts,clusters,nodes,workloads,stacks,distros}
```

For a list of subcommands for each command
```console
$ lava <command>
```

Here's an example of a cluster command with no arguments
```console
$ lava clusters

usage: lava clusters [-h] [--token TOKEN] [--api-key LAVA_API_KEY]
                      [--region REGION] [--tenant TENANT] [--version VERSION]
                      [--debug] [--endpoint ENDPOINT] [--auth-url AUTH_URL]
                      [--headless] [--user USER] [--password PASSWORD]
                      [--insecure]
                      {get,create,list,ssh_proxy,ssh,nodes,wait,resize,delete}
                      ...
lava clusters: error: too few arguments
```

### Authentication

Authentication requires a `username`, `tenant ID`, `region`, and `API key`. Username is your mycloud username.
Your `tenant ID` can be found on your mycloud control panel under the 'Account' tab. `region` is the location of your 
servers (DFW, LON, IAD, ORD). The `API key` can also be found in the mycloud control panel under 'Settings'.

```console
$ lava --user mycloud_username --tenant mytenant_id --region myserverregion --api-key myapikey authenticate

AUTH_TOKEN=3fb1a5a73973886b46bd7a94fa86c259
```

Alternatively, these values can be saved in a config file and passed in using [supernova](http://supernova.readthedocs.org/en/latest/index.html). You can use supernova with `lava` by specifying `lava` as the executable

```console
$ supernova -x lava dfw clusters list
```

### Clusters

With `lavaclient`, you can easily perform a variety of operations on your clusters including viewing, creating,
resizing and deleting.

To **list** all clusters

```console
$ lava clusters list

+--------------------------------------+-----------------+--------+--------------+---------------------------+
|                  ID                  |       Name      | Status |    Stack     |          Created          |
+--------------------------------------+-----------------+--------+--------------+---------------------------+
|         my-cluster-id-12345          |  myclustername  | ACTIVE | KAFKA_HDP2_2 | 2014-05-13 00:00:00+00:00 |
+--------------------------------------+-----------------+--------+--------------+---------------------------+
```

To **get** detailed information for a cluster

```console
$ lava clusters get --user mycloudusername --tenant mytenant_id --region myserverregion --token 3fb1a5a73973886b46bd7a94fa86c259

+----------------------------------------------------+
|                      Cluster                       |
+-------------+--------------------------------------+
| ID          |                  my-cluster-id-12345 |
| Name        |                        myclustername |
| Status      |                               ACTIVE |
| Stack       |                         KAFKA_HDP2_2 |
| Created     |            2014-05-13 00:00:00+00:00 |
| CBD Version |                                    2 |
| Username    |                      mycloudusername |
| Progress    |                                 1.00 |
+-------------+--------------------------------------+

+------------------------------------------------------------+
|                        Node Groups                         |
+-----------+-----------+-------+----------------------------+
|     ID    |   Flavor  | Count |         Components         |
+-----------+-----------+-------+----------------------------+
|   master  | hadoop1-4 |     1 |     [{name=Namenode}]      |
| secondary | hadoop1-4 |     1 | [{name=SecondaryNamenode}] |
|   slave   | hadoop1-7 |     1 |     [{name=Datanode},      |
|           |           |       |    {name=KafkaBroker},     |
|           |           |       |  {name=ZookeeperClient}]   |
| zookeeper | hadoop1-2 |     3 |  [{name=ZookeeperServer},  |
|           |           |       |  {name=ZookeeperClient}]   |
+-----------+-----------+-------+----------------------------+
```

To **create** a cluster you must specify the `name` of the cluster and the `stackID`. For stack options 

```console
$ lava stacks list --user mycloudusername --tenant mytenant_id --region myserverregion --token 3fb1a5a73973886b46bd7a94fa86c259

+---------------+---------------------------+--------+---------------------------------------------------+----------------------------------+
|       ID      |            Name           | Distro |                    Description                    |             Services             |
+---------------+---------------------------+--------+---------------------------------------------------+----------------------------------+
|   ALL_HDP2_2  | HDP 2.2 with all services | HDP2.2 | All components of the HDP distribution configured | [{name=HDFS, modes=[Secondary]}, |
|               |                           |        |             in a single cluster setup.            |      {name=YARN, modes=[]},      |
|               |                           |        |                                                   |   {name=MapReduce, modes=[]},    |
|               |                           |        |                                                   |      {name=Hive, modes=[]},      |
|               |                           |        |                                                   |      {name=Pig, modes=[]},       |
|               |                           |        |                                                   |     {name=Sqoop, modes=[]},      |
|               |                           |        |                                                   |     {name=Oozie, modes=[]},      |
|               |                           |        |                                                   |     {name=Flume, modes=[]},      |
|               |                           |        |                                                   |     {name=Storm, modes=[]},      |
|               |                           |        |                                                   |     {name=Kafka, modes=[]},      |
|               |                           |        |                                                   |   {name=Zookeeper, modes=[]},    |
|               |                           |        |                                                   |     {name=Falcon, modes=[]},     |
|               |                           |        |                                                   |     {name=Spark, modes=[]}]      |
| HADOOP_HDP2_2 |       Hadoop HDP 2.2      | HDP2.2 |   Core batch processing systems and interactive   | [{name=HDFS, modes=[Secondary]}, |
|               |                           |        |                querying with Hive.                |      {name=YARN, modes=[]},      |
|               |                           |        |                                                   |   {name=MapReduce, modes=[]},    |
|               |                           |        |                                                   |      {name=Hive, modes=[]},      |
|               |                           |        |                                                   |      {name=Pig, modes=[]},       |
|               |                           |        |                                                   |     {name=Sqoop, modes=[]},      |
|               |                           |        |                                                   |     {name=Oozie, modes=[]},      |
|               |                           |        |                                                   |     {name=Flume, modes=[]},      |
|               |                           |        |                                                   |     {name=Storm, modes=[]},      |
|               |                           |        |                                                   |     {name=Kafka, modes=[]},      |
|               |                           |        |                                                   |   {name=Zookeeper, modes=[]},    |
|               |                           |        |                                                   |     {name=Falcon, modes=[]},     |
|               |                           |        |                                                   |     {name=Spark, modes=[]}]      |
|  KAFKA_HDP2_2 |       Kafka HDP 2.2       | HDP2.2 | An individual Kafka stack serving as the backbone | [{name=HDFS, modes=[Secondary]}, |
|               |                           |        |      of a distributed message queuing system.     |      {name=YARN, modes=[]},      |
|               |                           |        |                                                   |   {name=MapReduce, modes=[]},    |
|               |                           |        |                                                   |      {name=Hive, modes=[]},      |
|               |                           |        |                                                   |      {name=Pig, modes=[]},       |
|               |                           |        |                                                   |     {name=Sqoop, modes=[]},      |
|               |                           |        |                                                   |     {name=Oozie, modes=[]},      |
|               |                           |        |                                                   |     {name=Flume, modes=[]},      |
|               |                           |        |                                                   |     {name=Storm, modes=[]},      |
|               |                           |        |                                                   |     {name=Kafka, modes=[]},      |
|               |                           |        |                                                   |   {name=Zookeeper, modes=[]},    |
|               |                           |        |                                                   |     {name=Falcon, modes=[]},     |
|               |                           |        |                                                   |     {name=Spark, modes=[]}]      |
|  STORM_HDP2_2 |   Storm + Kafka HDP 2.2   | HDP2.2 |    Real-time stream processing on HDP 2.2 with    | [{name=HDFS, modes=[Secondary]}, |
|               |                           |        |                    Storm/Kafka                    |      {name=YARN, modes=[]},      |
|               |                           |        |                                                   |   {name=MapReduce, modes=[]},    |
|               |                           |        |                                                   |      {name=Hive, modes=[]},      |
|               |                           |        |                                                   |      {name=Pig, modes=[]},       |
|               |                           |        |                                                   |     {name=Sqoop, modes=[]},      |
|               |                           |        |                                                   |     {name=Oozie, modes=[]},      |
|               |                           |        |                                                   |     {name=Flume, modes=[]},      |
|               |                           |        |                                                   |     {name=Storm, modes=[]},      |
|               |                           |        |                                                   |     {name=Kafka, modes=[]},      |
|               |                           |        |                                                   |   {name=Zookeeper, modes=[]},    |
|               |                           |        |                                                   |     {name=Falcon, modes=[]},     |
|               |                           |        |                                                   |     {name=Spark, modes=[]}]      |
+---------------+---------------------------+--------+---------------------------------------------------+----------------------------------+
```

**node-groups** must also be specified. node-groups consist of **flavor_id** and **count**. To view available flavors

```console
$ lava flavors list --user mycloudusername --tenant mytenant_id --region myserverregion --token 3fb1a5a73973886b46bd7a94fa86c259

+-------------+------------------------+--------+-------+-------+
|      ID     |          Name          |    RAM | VCPUs |  Disk |
+-------------+------------------------+--------+-------+-------+
|  hadoop1-15 | Medium Hadoop Instance |  15360 |     4 |  2500 |
|  hadoop1-30 | Large Hadoop Instance  |  30720 |     8 |  5000 |
|  hadoop1-60 | XLarge Hadoop Instance |  61440 |    16 | 10000 |
|  hadoop1-7  | Small Hadoop Instance  |   7680 |     2 |  1250 |
| onmetal-io1 |     OnMetal IO v1      | 131072 |    40 |  3200 |
+-------------+------------------------+--------+-------+-------+
```


```console
$ lava clusters create myclustername STORM_HDP2_2 --node-groups 'slave(flavor_id=hadoop1-7, count=1)' --user mycloudusername --tenant mytenantID --region myserverregion --token 3fb1a5a73973886b46bd7a94fa86c259

+----------------------------------------------------+
|                      Cluster                       |
+-------------+--------------------------------------+
| ID          | 9efce032-b904-4f12-9e6f-35aa4aeba8d8 |
| Name        |                        myclustername |
| Status      |                             BUILDING |
| Stack       |                         STORM_HDP2_2 |
| Created     |            2014-05-13 00:00:00+00:00 |
| CBD Version |                                    2 |
| Username    |                      mycloudusername |
| Progress    |                                 0.00 |
+-------------+--------------------------------------+

+------------------------------------------------------------+
|                        Node Groups                         |
+-----------+-----------+-------+----------------------------+
|     ID    |   Flavor  | Count |         Components         |
+-----------+-----------+-------+----------------------------+
|   master  | hadoop1-4 |     1 |     [{name=Namenode}]      |
| secondary | hadoop1-4 |     1 | [{name=SecondaryNamenode}] |
|   slave   | hadoop1-7 |     1 |     [{name=Datanode},      |
|           |           |       |    {name=KafkaBroker},     |
|           |           |       |  {name=ZookeeperClient}]   |
| zookeeper | hadoop1-2 |     3 |  [{name=ZookeeperServer},  |
|           |           |       |  {name=ZookeeperClient}]   |
+-----------+-----------+-------+----------------------------+
```

### Nodes

To display node information for a specific cluster

```console
$ lava nodes list my-cluster-id --user mycloudusername --tenant mytenant_id --region myserverregion --token 3fb1a5a73973886b46bd7a94fa86c259

+--------------------------------------+-------------+-----------+--------+-----------------+----------------+--------------------------------+
|                  ID                  |     Name    |    Role   | Status |    Public IP    |   Private IP   |           Components           |
+--------------------------------------+-------------+-----------+--------+-----------------+----------------+--------------------------------+
| d1ed20c6-0280-4c90-a339-cbe70f58f0dd |   master-1  |   master  | ACTIVE | xxx.xxx.xxx.xxx | xx.xxx.xxx.xxx |   [{nice_name=HDFS Namenode,   |
|                                      |             |           |        |                 |                | name=Namenode, uri=http://mast |
|                                      |             |           |        |                 |                |       er-1.local:xxxxx}]       |
| 5fa0a915-e656-4696-8f56-4c626019eb5e | zookeeper-2 | zookeeper | ACTIVE | xxx.xxx.xxx.xxx | xx.xxx.xxx.xxx | [{nice_name=Zookeeper Server,  |
|                                      |             |           |        |                 |                |     name=ZookeeperServer},     |
|                                      |             |           |        |                 |                |  {nice_name=Zookeeper Client,  |
|                                      |             |           |        |                 |                |     name=ZookeeperClient}]     |
| 1dd9998a-062a-4ca0-acd2-2a429010272d | zookeeper-3 | zookeeper | ACTIVE | xxx.xxx.xxx.xxx | xx.xxx.xxx.xxx | [{nice_name=Zookeeper Server,  |
|                                      |             |           |        |                 |                |     name=ZookeeperServer},     |
|                                      |             |           |        |                 |                |  {nice_name=Zookeeper Client,  |
|                                      |             |           |        |                 |                |     name=ZookeeperClient}]     |
| 92934c5a-55d9-423f-a331-607c6e706291 | zookeeper-1 | zookeeper | ACTIVE | xxx.xxx.xxx.xxx | xx.xxx.xxx.xxx | [{nice_name=Zookeeper Server,  |
|                                      |             |           |        |                 |                |     name=ZookeeperServer},     |
|                                      |             |           |        |                 |                |  {nice_name=Zookeeper Client,  |
|                                      |             |           |        |                 |                |     name=ZookeeperClient}]     |
| 3392bcf1-1fd8-4564-ba25-27f207465882 |   slave-1   |   slave   | ACTIVE | xxx.xxx.xxx.xxx | xx.xxx.xxx.xxx |   [{nice_name=HDFS Datanode,   |
|                                      |             |           |        |                 |                | name=Datanode, uri=http://slav |
|                                      |             |           |        |                 |                |       e-1.local:xxxxx},        |
|                                      |             |           |        |                 |                |    {nice_name=Kafka Broker,    |
|                                      |             |           |        |                 |                |       name=KafkaBroker},       |
|                                      |             |           |        |                 |                |  {nice_name=Zookeeper Client,  |
|                                      |             |           |        |                 |                |     name=ZookeeperClient}]     |
| 995f463e-26bd-427e-b041-baa31cf843c8 | secondary-1 | secondary | ACTIVE | xxx.xxx.xxx.xxx | xx.xxx.xxx.xxx |   [{nice_name=HDFS Secondary   |
|                                      |             |           |        |                 |                |           Namenode,            |
|                                      |             |           |        |                 |                | name=SecondaryNamenode, uri=ht |
|                                      |             |           |        |                 |                | tp://secondary-1.local:xxxxx}] |
+--------------------------------------+-------------+-----------+--------+-----------------+----------------+--------------------------------+
```
