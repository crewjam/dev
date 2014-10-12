FROM dockerfile/java:oracle-java6
MAINTAINER Ross Kinder <ross@kndr.org>

ADD http://stedolan.github.io/jq/download/linux64/jq /bin/jq
RUN git clone git://github.com/Netflix/SimianArmy.git
RUN (cd SimianArmy && ./gradlew build)

RUN chmod +x /bin/jq

ADD https://github.com/coreos/etcd/releases/download/v0.4.6/etcd-v0.4.6-linux-amd64.tar.gz /tmp/etcd.tar.gz
RUN cd /bin && tar -xzv --strip-components 1 -f /tmp/etcd.tar.gz
RUN rm /tmp/etcd.tar.gz

ADD chaos.properties /data/
ADD client.properties /data/
ADD conformity.properties /data/
ADD janitor.properties /data/
ADD log4j.properties /data/
ADD simianarmy.properties /data/
ADD volumeTagging.properties /data/

ADD main.sh /main
CMD ["/main"]