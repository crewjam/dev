FROM ubuntu:14.04
MAINTAINER Ross Kinder <ross@kndr.org>

RUN apt-get update && apt-get install -y \
  postgresql-9.3 \
  postgresql-contrib-9.3

ADD https://github.com/coreos/etcd/releases/download/v0.4.6/etcd-v0.4.6-linux-amd64.tar.gz /tmp/etcd.tar.gz
RUN cd /bin && tar -xzv --strip-components 1 -f /tmp/etcd.tar.gz
RUN rm /tmp/etcd.tar.gz

VOLUME ["/data"]
EXPOSE 5432

ADD main /main
CMD ["/main"]
