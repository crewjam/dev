
btsync
======

This container is used to maintain a replicated data volume across availability
zones using bittorrent. This can be used to simulate high-availability for
single-master or central services like redis and postgres.

Example fleet unit (call it frob-data-volume@.service):

    [Unit]
    Description=frob2 data volume
    
    [Service]
    TimeoutStartSec=0
    ExecStartPre=/usr/bin/mkdir -p /var/lib/data/%p
    ExecStartPre=/usr/bin/docker pull crewjam/btsync
    ExecStartPre=-/usr/bin/etcdctl mkdir /services/%p
    
    # Generate a secret if we don't already have one
    ExecStartPre=/bin/bash -ex -c '\
      /usr/bin/etcdctl get /services/%p/btsync_secret || (\
        /usr/bin/docker run crewjam/btsync btsync --generate-secret | \
          /usr/bin/etcdctl mk /services/%p/btsync_secret;\
        sleep 10;\
      )\
      '
    
    # Run the sync service
    ExecStart=/bin/bash -c '\
      docker run --rm --name %p \
        -v /var/lib/data/%p:/data \
        crewjam/btsync \
        start-btsync $(/usr/bin/etcdctl get /services/%p/btsync_secret) \
      '
    
    ExecStop=/usr/bin/docker stop %p
    
    [X-Fleet]
    X-ConditionMachineOf=frob@%i.service

Note: the original idea for this came from this Century Link Lab blog: 
http://www.centurylinklabs.com/persistent-distributed-filesystems-in-docker-without-nfs-or-gluster/