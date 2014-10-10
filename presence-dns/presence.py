#!/usr/bin/python

import argparse
import os
import re
import sys

import boto
import etcd
import urllib3

def Configure(options, client):
  aws_access_key_id = client.get("/secrets/aws_access_key_id").value
  aws_secret_access_key = client.get("/secrets/aws_secret_access_key").value

  etcd_prefix = "/services/{}".format(options.service_name)

  r53 = boto.connect_route53(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key)
  zone_name = str(client.get(etcd_prefix + "/route53_zone").value)
  zone = r53.get_zone(zone_name)
  if zone is None:
    raise RuntimeError("cannot find zone {}".format(zone_name))

  dns_name = client.get(etcd_prefix + "/dns_name").value
  try:
    ttl = int(client.get(etcd_prefix + "/dns_ttl").value)
  except KeyError:
    ttl = "600"
  a = zone.get_a(dns_name)

  resource_records = []
  for instance in client.get(etcd_prefix + "/instances/").children:
    try:
      address = client.get(instance.key + "/public_ip").value
    except KeyError:
      print instance.key, "no public_ip"
      continue

    resource_records.append(address)

  if a is None:
    print "add", dns_name, "IN A", resource_records
    zone.add_a(dns_name, resource_records, ttl=ttl)
  elif set(map(str, a.resource_records)) != set(resource_records):
    print "update", dns_name, "IN A", resource_records
    zone.update_a(dns_name, resource_records, ttl=ttl)
  else:
    print "no change", dns_name, "IN A", resource_records


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--etcd")
  parser.add_argument("--service-name", default=os.environ.get("SERVICE_NAME"))
  options = parser.parse_args(args)

  if options.etcd is None:
    options.etcd, = re.match("http://(.*):4001",
      os.environ.get("ETCDCTL_PEERS")).groups()

  client = etcd.Client(host=options.etcd)

  while True:
    Configure(options, client=client)

    try:
      client.read("/services/{}".format(options.service_name),
        recursive=True, wait=True, waitIndex=0, timeout=0)
    except urllib3.exceptions.ReadTimeoutError:
      pass


if __name__ == "__main__":
  Main()
