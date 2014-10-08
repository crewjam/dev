FROM ubuntu:14.04
MAINTAINER Ross Kinder <ross@kndr.org>
RUN apt-get update && apt-get install -y \
  default-jre-headless \
  git \
  postgresql-client

ADD https://gerrit-releases.storage.googleapis.com/gerrit-2.9.1.war /gerrit.war

RUN mkdir /data
RUN java -jar /gerrit.war init --batch -d /data --no-auto-start

RUN ln -sf /dev/stderr /data/logs/error_log
RUN ln -sf /dev/stdout /data/logs/sshd_log

# clobber the gerrit config. set the URL to localhost:8080
ADD gerrit.config /gerrit.config
ADD initialize /initialize
ADD main /main

EXPOSE 8080 29418
CMD ["/main"]
# CMD ["/data/bin/gerrit.sh", "supervise", "-d", "/data"]
