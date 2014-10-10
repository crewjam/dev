
btsync
======

This container is used to maintain a replicated data volume across availability
zones using bittorrent. This can be used to simulate high-availability for
single-master or central services like redis and postgres.

Example fleet unit (call it frob-data-volume@.service):

    [Unit]
    Description=btsync data volume gerrit-db
    After=etcd-amb.service
    After=etcd.service
    BindsTo=gerrit-db-pod@%i.service
    
    [Service]
    EnvironmentFile=/etc/environment
    TimeoutStartSec=120
    Restart=always
    RestartSec=15sec
    StartLimitInterval=10
    StartLimitBurst=5
    ExecStartPre=-/usr/bin/docker kill gerrit-db-data-volume
    ExecStartPre=-/usr/bin/docker rm gerrit-db-data-volume
    ExecStartPre=-/usr/bin/docker pull crewjam/btsync
    ExecStart=/usr/bin/docker run --rm --name gerrit-db-data-volume \
      -e 'ETCDCTL_PEERS=http://${COREOS_PRIVATE_IPV4}:4001' \
      -e VOLUME_NAME=gerrit-db \ 
      -v /data0/gerrit-db-data-volume:/data \
      crewjam/btsync
    ExecStop=/usr/bin/docker kill gerrit-db-data-volume
    
    [X-Fleet]
    X-ConditionMachineOf=gerrit-db-pod@%i.service

Note: the original idea for this came from this Century Link Lab blog: 
http://www.centurylinklabs.com/persistent-distributed-filesystems-in-docker-without-nfs-or-gluster/