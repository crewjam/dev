FROM ubuntu:14.04

RUN apt-get update && apt-get install -y curl

ADD http://download-lb.utorrent.com/endpoint/btsync/os/linux-x64/track/stable \
  /usr/bin/btsync.tar.gz
RUN cd /usr/bin && tar -xzvf btsync.tar.gz && rm btsync.tar.gz

RUN mkdir -p /btsync/.sync
RUN mkdir -p /var/run/btsync
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 8888
EXPOSE 55555

ADD main /main
RUN chmod +x /main

CMD ["/main"]
