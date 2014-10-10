presence-dns
============

This container registers the IP address of a service into an A-record in the DNS
via AWS Route53. The dns name and Route 53 zone name must be specified in etcd 
under ``/services/$service_name/dns_name`` and 
``/services/$service_name/route53_zone`` respectively.

We get the pool of running instances from the ``public_ip`` key under
``/services/$service_name/instances`` where *$service_name* is given by 
``--service-name`` or ``$SERVICE_NAME``.

You may optionally specify the ttl with ``/services/$service_name/dns_ttl``.

