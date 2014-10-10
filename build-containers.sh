#!/bin/bash
set -ex

source_dir=$(dirname "${BASH_SOURCE}")

# TODO(ross): fix it so others can build containers (!)
[ "$USER" == "ross" ]  ||\
  (echo "TODO: this program will push containers to the docker registry. If "\
    "you are not ross you may have trouble with this."; exit 1)

for path in $(ls $source_dir/*/build.sh); do
  $path
done
