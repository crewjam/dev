FROM ubuntu:14.04
MAINTAINER Ross Kinder <ross@kndr.org>

FROM dockerfile/java:oracle-java7

RUN apt-get update && apt-get install -y git postgresql-client

ADD https://github.com/coreos/etcd/releases/download/v0.4.6/etcd-v0.4.6-linux-amd64.tar.gz /tmp/etcd.tar.gz
RUN cd /bin && tar -xz --strip-components 1 -f /tmp/etcd.tar.gz
RUN rm /tmp/etcd.tar.gz

ADD https://gerrit-releases.storage.googleapis.com/gerrit-2.9.1.war /gerrit.war

RUN mkdir /data/logs
RUN ln -sf /dev/stderr /data/logs/error_log
RUN ln -sf /dev/stdout /data/logs/sshd_log

# clobber the gerrit config. set the URL to localhost:8080
ADD gerrit.config /gerrit.config
ADD main /main

EXPOSE 8080 29418
CMD ["/main"]
