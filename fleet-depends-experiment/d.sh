#!/bin/bash
set -ex
services="d-pod@1.service d@1.service d-data-volume@1.service d-db-amb@1.service d-presence@1.service"
fleetctl destroy *.service $services
fleetctl submit *.service
fleetctl start $services
