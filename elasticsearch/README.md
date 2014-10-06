
elasticsearch
=============

This container launches elasticsearch with configuration parameters derived from
etcd. It reads configuration from etcd starting at ``$prefix`` which defaults to 
``/services/elasticsearch``. It fetches or generates a cluster name from 
``$prefix/cluster_name``. It searches for instances of the master from 
``$prefix/master/instances`` and populates the initial node list with those 
hosts. It specifies that data be stored in ``/data0``, ``/data1``, etc. if 
present.
