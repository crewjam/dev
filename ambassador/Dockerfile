FROM ubuntu:14.04
MAINTAINER Ross Kinder <ross@kndr.org>
RUN apt-get update && apt-get install -y \
  libffi-dev \
  libssl-dev \
  python-boto \
  python-dev \
  python-pip \
  python-requests
RUN pip install python-etcd
RUN apt-get update && apt-get install -y \
  haproxy

COPY ambassador.py /bin/ambassador
CMD /bin/ambassador
