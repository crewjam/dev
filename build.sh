#!/bin/bash
set -ex

for path in $(ls ./*/build.sh); do
  $path
done
