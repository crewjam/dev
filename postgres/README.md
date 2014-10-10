postgres
========

This container implements a pseudo-replicated postgres database. In ``/main``
we use etcd to hold an election to determine which instance of the service will
be the master node. The winner of the election launches postgres. The other 
nodes block trying to win the election and if they do, they launch postgres.

To use it you must set ``$SERVICE_NAME``, ``$INSTANCE`` and ``$PRIVATE_IP`` in
the environment.

For example, with three instances running, etcd might look like this:

    /services/postgres/master = "2"
    /services/postgres/instances/1/private_ip = "10.0.19.22"
    /services/postgres/instances/2/private_ip = "10.0.21.81"
    /services/postgres/instances/3/private_ip = "10.0.76.34"

**Warning** 

The ``master`` key is written without a TTL, but the script attempts
to clean it up at exit time. If this cleanup doesn't happen for some reason 
then you might end up with nobody winning the election. 

To clean up, just delete the master key and somebody else will win (but make
super duper sure there is no other master running first):

    etcdctl rm /services/postgres/master

