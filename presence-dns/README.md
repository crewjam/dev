
presence-dns
============

This container registers the IP address of a service into an A-record in the DNS
via route53. 

It is intended to be bound to a service with ``BindsTo=`` so it is started and 
stopped along with the service.

At startup is program writes values in ``$prefix/instances/$instance/`` where
``$prefix`` and ``$instance`` are specified by ``--etcd-prefix`` and 
``--instance`` respectively. The values are given by the ``--host``, 
``--public-ip``, ``--private-ip``, and ``--port`` options. 

Values are written with a default ttl of 60 seconds (``--ttl``). This program 
refreshes the keys with an interval of two thirds of the ttl. If the program is 
killed by ``SIGTERM`` or ``SIGINT``, it removes the values from route53.

