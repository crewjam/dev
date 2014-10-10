FROM ubuntu:14.04
MAINTAINER Ross Kinder <ross@kndr.org>
RUN apt-get update && apt-get install -y build-essential curl git libpcre3-dev libssl-dev

RUN curl http://nginx.org/download/nginx-1.6.2.tar.gz | tar -vxzf - -C /
RUN git clone https://github.com/yaoweibin/nginx_tcp_proxy_module
RUN cd nginx_tcp_proxy_module && git reset --hard 816d03d8b2949ab45ba18b96c843563d387491b5
RUN cd nginx-1.6.2 && patch -p1 < ../nginx_tcp_proxy_module/tcp.patch
RUN cd nginx-1.6.2 && ./configure \
  --with-http_ssl_module \
  --with-http_spdy_module \
  --with-http_auth_request_module \
  --add-module=../nginx_tcp_proxy_module
RUN cd nginx-1.6.2 && make && make install



