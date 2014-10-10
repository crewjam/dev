
presence
========

This container announces the presence of a service in etcd. It is intended to be
bound to a service with ``BindsTo=`` so it is started and stopped along with the
service.

At startup is program writes values in ``$prefix/instances/$instance/`` where
``$prefix`` and ``$instance`` are specified by ``--etcd-prefix`` and 
``--instance`` respectively. The values are given by the ``--host``, 
``--public-ip``, ``--private-ip``, and ``--port`` options. 

Values are written with a default ttl of 60 seconds (``--ttl``). This program 
refreshes the keys with an interval of two thirds of the ttl. If the program is 
killed by ``SIGTERM`` or ``SIGINT``, it removes the values from etcd.

Example unit file:

    [Unit]
    Description=gerrit-app-presence
    After=gerrit-app@%i.service
    BindsTo=gerrit-app@%i.service
    
    [Service]
    EnvironmentFile=/etc/environment
    TimeoutStartSec=120
    Restart=always
    RestartSec=15sec
    StartLimitInterval=10
    StartLimitBurst=5
    ExecStartPre=-/usr/bin/docker kill gerrit-app-presence
    ExecStartPre=-/usr/bin/docker rm gerrit-app-presence
    ExecStartPre=-/usr/bin/docker pull crewjam/presence
    ExecStart=/usr/bin/docker run --rm --name gerrit-app-presence \
      -e INSTANCE=%i \
      -e HOSTNAME=%H \
      -e 'PUBLIC_IP=${COREOS_PUBLIC_IPV4}' \
      -e 'PRIVATE_IP=${COREOS_PRIVATE_IPV4}' \
      -e 'ETCDCTL_PEERS=http://${COREOS_PRIVATE_IPV4}:4001' \
      -e SERVICE_NAME=gerrit-app \
      crewjam/presence
    ExecStop=/usr/bin/docker kill gerrit-app-presence
    
    [X-Fleet]
    X-ConditionMachineOf=gerrit-app@%i.service

