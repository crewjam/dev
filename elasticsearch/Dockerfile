FROM dockerfile/elasticsearch
MAINTAINER Ross Kinder <ross@kndr.org>

RUN apt-get update && apt-get install -y \
  libffi-dev \
  libssl-dev \
  python-dev \
  python-pip \
  python-requests
RUN pip install python-etcd

RUN /elasticsearch/bin/plugin --install mobz/elasticsearch-head
RUN /elasticsearch/bin/plugin --install elasticsearch/elasticsearch-cloud-aws/2.3.0

COPY main.py /main
CMD ["/main"]