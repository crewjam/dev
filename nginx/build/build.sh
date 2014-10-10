#!/bin/bash
set -ex
docker build -t crewjam/nginx-build .
docker run crewjam/nginx-build cat /usr/local/nginx/sbin/nginx > nginx

docker run crewjam/nginx-build md5sum /usr/local/nginx/sbin/nginx
md5sum nginx
chmod +x nginx