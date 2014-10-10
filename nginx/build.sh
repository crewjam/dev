#!/bin/bash
set -ex

package_dir=$(dirname "${BASH_SOURCE}")

docker build -t crewjam/nginx-build $package_dir/build

# fetch the built binary from the container
docker run crewjam/nginx-build cat /usr/local/nginx/sbin/nginx > $package_dir/build/nginx
docker run crewjam/nginx-build md5sum /usr/local/nginx/sbin/nginx
md5sum $package_dir/build/nginx
chmod +x $package_dir/build/nginx

docker build -t crewjam/nginx $package_dir
docker push crewjam/nginx
