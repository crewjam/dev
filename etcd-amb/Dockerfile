FROM ubuntu:14.04
MAINTAINER Ross Kinder <ross@kndr.org>
RUN apt-get update && apt-get install -y python haproxy

COPY ambassador.py /bin/ambassador
CMD /bin/ambassador
