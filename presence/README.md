
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
    Description=mariadb presence service
    BindsTo=mariadb@%i.service
    
    [Service]
    EnvironmentFile=/etc/environment
    ExecStartPre=-/usr/bin/docker kill mariadb-presence-%i
    ExecStartPre=-/usr/bin/docker rm mariadb-presence-%i
    ExecStartPre=/usr/bin/docker pull crewjam/presence
    ExecStart=/bin/sh -c '/usr/bin/docker run --rm --name mariadb-presence-%i \
      crewjam/presence /bin/presence \
        --etcd-prefix=/services/mariadb \
        --etcd=${COREOS_PRIVATE_IPV4} \
        --instance=%i \
        --port="$(expr 3306 + %i)" \
      '
    ExecStop=/usr/bin/docker kill mariadb-presence-%i
    TimeoutStartSec=0
    
    [X-Fleet]
    X-ConditionMachineOf=mariadb@%i.service
