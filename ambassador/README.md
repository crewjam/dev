
generic etcd-backed ambassador
==============================

This program owns an haproxy service that proxies between a local port and the
services defined in etcd. Whenever the service configuration changes, haproxy 
is reconfigured and sent `SIGHUP`.

Example:

    docker run -p 5432:5432 --name mysql-to-app-amb crewjam/ambassador \
      --etcd-prefix=/services/mysql \
      --master-ony \
      --port=5432
 
The ambassador reads the service configuration from the specified etcd path. 
There must be a subkey of the prefix called ``instances`` and one subkey for 
each instance under that. The instance key must have a value ``private_ip``
(or ``public_ip`` if ``--public`` is given). 

If ``--master-only`` is given then the ambassador tracks the ``master`` key 
whose value contains the name of the current "master" in the cluster. In this 
mode traffic is only proxied to the master and not to other instances.

Example:

    /services/mysql/master = "2"
    /services/mysql/instances/1/private_ip = "10.0.19.22"
    /services/mysql/instances/2/private_ip = "10.0.21.81"
    /services/mysql/instances/3/private_ip = "10.0.76.34"

Use with fleet and systemd
--------------------------

Consider a service that requires mysql:
  
    [Unit]
    Description=loadtest
    BindTo=mysql-loadtest-amb@%i.service
    
    [Service]
    EnvironmentFile=/etc/environment
    ExecStartPre=-/usr/bin/docker kill %p
    ExecStartPre=-/usr/bin/docker rm %p
    ExecStartPre=/usr/bin/docker pull crewjam/loadtest
    ExecStart=/bin/bash -c '\
      /usr/bin/docker run --rm --name %p \
        crewjam/loadtest /main --server=${COREOS_PRIVATE_IPV4} --batch-size=0'
    ExecStop=/usr/bin/docker kill %p
    TimeoutStartSec=0
    
    [X-Fleet]
    X-ConditionMachineOf=mysql-loadtest-amb@%i.service

Here is a unit that can be used to start the ambassador:
    
    [Unit]
    Description=Mysql ambassador for loadtest
    Before=loadtest@%i.service
    
    [Service]
    EnvironmentFile=/etc/environment
    TimeoutStartSec=0
    ExecStartPre=-/usr/bin/docker kill mysql-loadtest-amb
    ExecStartPre=-/usr/bin/docker rm mysql-loadtest-amb
    ExecStartPre=/usr/bin/docker pull crewjam/ambassador
    ExecStart=/usr/bin/docker run --rm \
      --name mysql-loadtest-amb \
      -p 5432:5432 \
      crewjam/ambassador \
      /bin/ambassador \
        --etcd-prefix=/services/mysql \
        --master-only \
        --etcd=${COREOS_PRIVATE_IPV4} \ 
        --port=5432
    ExecStop=/usr/bin/docker kill mysql-loadtest-amb


