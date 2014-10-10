nginx
=====

This container launches nginx. 

The main command builds ``/etc/nginx/nginx.conf`` from 
``/etc/nginx/nginx.conf.tmpl`` which is a jinja2 template. The program monitors
etcd and whenever the configuration changes it sends nginx a ``SIGHUP``.
 
The following settings are needed for the core server:
 
  * ``/services/nginx/dns_name`` - the DNS name of the server, i.e. *example.com*
  * ``/services/nginx/ssl_cert`` - the SSL certificate
  * ``/services/nginx/ssl_key`` - the SSL key
  
In addition *main* reads the following::

  * ``/services/gerrit-app/instances/*/private_ip`` to determine which nodes
    are running the *gerrit* application.

This version of nginx is build with `nginx_tcp_proxy_module` which allows us to
do raw tcp proxying on the same box. This simplifies providing access to the
gerrit sshd. Because nginx has to be compiled by hand, we have a separate 
container to generate the nginx binary, which we copy into the main container 
at build time.

**Why write a program and not use `confd`?**

Because the go template language it uses was confusing to us. We are used to
jinja2 and find them easier to grok. Also we like the idea of the configure 
tool being the parent of the main service process. (Perhaps something like
this could make a nice standalone alternative to confd)


