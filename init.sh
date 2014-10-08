#!/bin/bash
set -ex

cd $(dirname "${BASH_SOURCE}")
units=$(ls units)
for unit in $units; do
   fleetctl destroy $unit
   fleetctl submit units/$unit
done

units="\
  gerrit@1.service
  gerrit@2.service
  gerrit@3.service
  gerrit-data-volume@1.service
  gerrit-data-volume@2.service
  gerrit-data-volume@3.service
  gerrit-postgres-amb@1.service
  gerrit-postgres-amb@2.service
  gerrit-postgres-amb@3.service
  gerrit-presence@1.service
  gerrit-presence@2.service
  gerrit-presence@3.service
  "
fleetctl start $units
