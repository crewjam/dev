nginx
=====

This container launches nginx. 

It uses confd to generate a configuration from the provided template and the 
settings in etcd. The following settings are needed for the core server:
 
  * ``/services/nginx/dns_name`` - the DNS name of the server, i.e. *example.com*
  * ``/services/nginx/ssl_cert`` - the SSL certificate
  * ``/services/nginx/ssl_key`` - the SSL key
  
In addition confd reads the following::

  * ``/services/gerrit-app/instances/*/private_ip`` to determine which nodes
    are running the *gerrit* application.


