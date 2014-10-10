#!/usr/bin/python -u

import argparse
import time
import os
import re
import signal
import sys

import etcd

def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--etcd")
  parser.add_argument("--etcd-prefix")
  parser.add_argument("--instance", default=os.environ.get("INSTANCE"))
  parser.add_argument("--host", default=os.environ.get("HOSTNAME"))
  parser.add_argument("--public-ip", default=os.environ.get("PUBLIC_IP"))
  parser.add_argument("--private-ip", default=os.environ.get("PRIVATE_IP"))
  parser.add_argument("--port", type=int, default=os.environ.get("PORT"))
  parser.add_argument("--ttl", type=int, default=60)
  options = parser.parse_args(args)

  if options.etcd is None:
    options.etcd, = re.match("http://(.*):4001",
      os.environ.get("ETCDCTL_PEERS")).groups()

  if options.etcd_prefix is None:
    options.etcd_prefix = "/services/{}".format(os.environ.get("SERVICE_NAME"))

  client = etcd.Client(host=options.etcd)
  prefix = options.etcd_prefix + "/instances/" + str(options.instance)

  if options.host is not None:
    print prefix + "/host", "=", options.host
  if options.port is not None:
    print prefix + "/port",  "=", str(options.port)
  if options.private_ip is not None:
    print prefix + "/private_ip",  "=", options.private_ip
  if options.public_ip is not None:
    print prefix + "/public_ip",  "=", options.public_ip

  def Clear():
    client.delete(prefix, recursive=True)
    print "cleared", prefix
  signal.signal(signal.SIGTERM, Clear)
  signal.signal(signal.SIGINT, Clear)

  while True:
    if options.host is not None:
      client.set(prefix + "/host", options.host, ttl=options.ttl)
    if options.port is not None:
      client.set(prefix + "/port", str(options.port), ttl=options.ttl)
    if options.private_ip is not None:
      client.set(prefix + "/private_ip", options.private_ip, ttl=options.ttl)
    if options.public_ip is not None:
      client.set(prefix + "/public_ip", options.public_ip, ttl=options.ttl)
    time.sleep(options.ttl * 2 / 3)


if __name__ == "__main__":
  Main()
