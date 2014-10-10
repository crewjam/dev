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
RUN pip install jinja2

ADD build/nginx /bin/nginx

RUN mkdir -p /etc/nginx
ADD nginx.conf.tmpl /etc/nginx/nginx.conf.tmpl

EXPOSE 80 443 1022

COPY main.py /main


CMD /main
