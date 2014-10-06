
etcd discovery for slaves
=========================

CoreOS describe a production architecture with a small number (<= 9) of etcd
nodes while the remaining nodes are etcd clients. Unfortunately neither coreos
nor etcd provide a way for slaves to discover the set of etcd servers.

https://coreos.com/docs/cluster-management/setup/cluster-architectures/#production-cluster-with-central-services

The problem is that there are zillions of places where it is assumed that etcd
is available at 127.0.0.1:4001. Rather than fight with configuration, we have an
ambassador that proxies access to the etcd port on localhost to the real etcd 
servers. 

This program polls the global etcd discovery service to build a list of etcd 
peers and set up the proxy appropriately.

An example unit file:

    [Unit]
    Description=etcd discovery container
    Before=fleet.service
    Conflicts=etcd.service
    
    [Service]
    ExecStartPre=-/usr/bin/docker kill etcd-discovery
    ExecStartPre=-/usr/bin/docker rm etcd-discovery
    ExecStartPre=/usr/bin/docker pull crewjam/etcd-discover
    ExecStart=/usr/bin/docker run --rm --name etcd-discovery \
      -p 4001:4001 \ 
      -e ETCD_DISCOVERY_URL=https://discovery.etcd.io/45529213ac74477b4bcf9ace49883408 \ 
      crewjam/etcd-discover
    ExecStop=/usr/bin/docker kill etcd-discovery
