#!/usr/bin/python -u

import argparse
import time
import signal
import socket
import subprocess
import sys

import etcd


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--etcd", default="localhost")
  parser.add_argument("--etcd-prefix")
  parser.add_argument("--instance")
  parser.add_argument("--host")
  parser.add_argument("--public-ip")
  parser.add_argument("--private-ip")
  parser.add_argument("--port", type=int, default=None)
  parser.add_argument("--ttl", type=int, default=60)
  options = parser.parse_args(args)

  client = etcd.Client(host=options.etcd)
  prefix = options.etcd_prefix + "/instances/" + str(options.instance)

  def Clear():
    client.delete(prefix, recursive=True)
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
