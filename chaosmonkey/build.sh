#!/bin/bash
set -ex

package_dir=$(dirname "${BASH_SOURCE}")
tag=crewjam/$(basename $(dirname "${BASH_SOURCE}"))

docker pull $tag || true
docker build -t $tag $package_dir
docker push $tag
printf \a