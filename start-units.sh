#!/bin/bash
set -e

source_dir=$(dirname "${BASH_SOURCE}")
units_dir=$source_dir/units

required_keys="
  /secrets/aws_access_key_id
  /secrets/aws_secret_access_key
  /services/nginx/dns_name
  /services/nginx/route53_zone
  /services/nginx/ssl_cert
  /services/nginx/ssl_keydd"

template_units="
  gerrit-app-presence@.service
  gerrit-app@.service
  gerrit-data-volume-git@.service
  gerrit-db-data-volume@.service
  gerrit-db-gerrit-amb@.service
  gerrit-db-pod@.service
  gerrit-db@.service
  gerrit-pod@.service
  nginx-presence@.service
  nginx@.service"

singleton_units="
  nginx-presence-dns.service"

[ -f secrets.sh ] && . secrets.sh

ok="yes"
for key in $required_keys; do
  echo -n "checking $key "
  if [ -z "$(etcdctl get $key 2>/dev/null || true)" ] ; then
    echo "missing"
    ok="no"
  else
    echo "present"
  fi
done

if [ ! $ok == yes ] ; then
  echo "ERROR: you are missing configuration. Edit secrets.sh or run set the "\
    "missing keys in etcd.";
  exit 1
fi

fleetctl destroy $template_units
(cd $units_dir && fleetctl submit $template_units)

units="
  $singleton_units
  $(echo $template_units | sed 's/@./@1/g')
  $(echo $template_units | sed 's/@./@2/g')
  $(echo $template_units | sed 's/@./@3/g')"
(cd $units_dir && fleetctl start $units)
