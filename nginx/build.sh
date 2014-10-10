#!/bin/bash
set -ex

(cd build && ./build.sh)

docker build -t crewjam/nginx .
docker push crewjam/nginx
