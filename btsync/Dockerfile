FROM ubuntu:14.04

RUN apt-get update && apt-get install -y curl

ADD https://github.com/coreos/etcd/releases/download/v0.4.6/etcd-v0.4.6-linux-amd64.tar.gz /tmp/etcd.tar.gz
RUN cd /bin && tar -xzv --strip-components 1 -f /tmp/etcd.tar.gz
RUN rm /tmp/etcd.tar.gz

ADD http://download-lb.utorrent.com/endpoint/btsync/os/linux-x64/track/stable \
  /tmp/btsync.tar.gz
RUN cd /bin && tar -xzvf /tmp/btsync.tar.gz
RUN rm /tmp/btsync.tar.gz

RUN mkdir -p /btsync/.sync
RUN mkdir -p /var/run/btsync
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 8888
EXPOSE 55555

ADD main /main
RUN chmod +x /main

CMD ["/main"]
