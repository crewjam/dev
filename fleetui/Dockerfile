FROM ubuntu:14.04
MAINTAINER Ross Kinder <ross@kndr.org>

RUN apt-get update && apt-get install -y git python-flask
RUN git clone https://github.com/coreos/fleet
RUN apt-get install -y golang
RUN (cd fleet; ./build)

EXPOSE 4002
COPY templates /templates
COPY fleetui.py /fleetui
CMD /fleetui
