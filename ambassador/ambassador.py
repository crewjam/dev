#!/usr/bin/python -u

import argparse
import signal
import subprocess
import sys
from os.path import isfile

import etcd

CONFIGURATION  = """
global
  log 127.0.0.1 local0
  log 127.0.0.1 local1 notice
  maxconn 4096
  chroot /var/lib/haproxy
  user haproxy
  group haproxy

defaults
  log global
  option dontlognull
  contimeout 5000
  clitimeout 50000
  srvtimeout 50000

listen outside :{port}
  mode tcp
  option tcplog
  balance leastconn

{servers}
"""

SERVER_CONFIGURATION = "  server {name} {address}:{port}\n"

CHANGED = object()
NOT_CHANGED = object()

def Configure(options, client):
  if options.master_only:
    try:
      master_instance = client.get(options.etcd_prefix + "/master").value
    except KeyError:
      master_instance = None
    print master_instance, "is the master"

  try:
    children = client.get(options.etcd_prefix + "/instances/").children
  except KeyError:
    client.write(options.etcd_prefix + "/instances/", "", dir=True)
    children = []

  server_configurations = []
  for instance_key in children:
    instance = instance_key.key.split("/")[-1]

    print "considering", instance
    name = "server-" + instance

    if options.public:
      key = instance_key.key + "/public_ip"
    else:
      key = instance_key.key + "/private_ip"

    try:
      address = client.get(key).value
    except KeyError:
      continue

    try:
      port = int(client.get(instance_key.key + "/port").value)
    except KeyError:
      port = options.port

    if options.master_only and master_instance != instance:
      print instance, "is excluded because it is not the master (%r != %r)" % (master_instance, instance)
      continue

    if instance in options.exclude_instance:
      print instance, "is excluded"
      continue

    server_configuration = SERVER_CONFIGURATION.format(
      name=name, address=address, port=port)
    server_configurations.append(server_configuration)

  server_configurations.sort()
  configuration = CONFIGURATION.format(port=options.port,
    servers="".join(server_configurations))

  if isfile("/haproxy.cfg") and file("/haproxy.cfg").read() == configuration:
    print "configuration is unchanged"
    return NOT_CHANGED

  with file("/haproxy.cfg", "w") as configuration_file:
    configuration_file.write(configuration)
  print configuration

  return CHANGED


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--etcd", default="localhost")
  parser.add_argument("--etcd-prefix")
  parser.add_argument("--master-only", action="store_true", default=False)
  parser.add_argument("--public", action="store_true", default=False)
  parser.add_argument("--exclude-instance", action="append", default=[])
  parser.add_argument("--port", type=int)
  options = parser.parse_args(args)

  client = etcd.Client(host=options.etcd)

  Configure(options, client=client)
  proc = subprocess.Popen(["haproxy", "-f", "/haproxy.cfg"])

  while True:
    client.read(options.etcd_prefix, recursive=True, wait=True, waitIndex=0)

    state = Configure(options, client=client)
    if state is CHANGED:
      proc.send_signal(signal.SIGHUP)

if __name__ == "__main__":
  Main()
