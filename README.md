dev
===

Example infrastructure for building a development environment with CoreOS and 
Docker.

Building Containers
-------------------

Each container has a build.sh script that can be used to build, tag and push
the container to the docker registry. 

    for container in ambassador etcd-amb presence; do
      ./$container/build.sh
    done

Cloud Formation
---------------

Cloud Formation is mechanism and format for declaring AWS resources. Rather than
hand produce a repetitive document, we have code that produces a cloudformation
document you can use to create a cluster in AWS. For convenience you can also 
build and update clusters with the tool as well. 

    cloudformation/build.py --dns-name dev.example.com \
      --key=alice@example.com \
      build

Open Issues
-----------

- A couple of times during this process, I've encountered a case where all
  etcd nodes are down and I can't figure out how to recover from this. While
  restarting the etcds they seem not to think they are really the master.

- Exactly how to get all the fleet units configured when launching a cluster or
  adding a service is still rather an open question. I'd like to figure out 
  
Configuration
-------------

Set up AWS keys:

    $ etcdctl set /secrets/aws_access_key_id XXXXXXXXXXXXXXXXXXXX
    $ etcdctl set /secrets/aws_secret_access_key yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
    
Set up nginx service:
    
    $ etcdctl set /services/nginx/route53_zone dev.example.com
    $ etcdctl set /services/nginx/dns_name dev.example.com
    $ etcdctl set /services/nginx/dns_ttl 300
  
Nginx self-signed certificate:

    openssl genrsa -des3 -out server.key 1024
    openssl req -new -key server.key -out server.csr
    cp server.key server.key.org
    openssl rsa -in server.key.org -out server.key
    openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
    cat server.crt | etcdctl set /services/nginx/ssl_cert
    cat server.key | etcdctl set /services/nginx/ssl_key
