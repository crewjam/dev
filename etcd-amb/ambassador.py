#!/usr/bin/python -u

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import traceback
import urllib2
from os.path import isfile

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

def Configure(options):
  server_configurations = []

  # Be moderately persistent trying to fetch from the discovery URL
  for try_ in range(60):
    try:
      data = json.load(urllib2.urlopen(options.discovery_url))
      hosts = [item["value"] for item in data["node"]["nodes"]]
      assert hosts
    except Exception:
      traceback.print_exc()
      time.sleep(5)
      continue
    break

  # each host is something like http://10.10.6.247:7001
  # we need it to be: 10.10.6.247:4001
  # (srsly, wtf?)
  hosts = [host.replace(":7001", "") for host in hosts]
  hosts = [host.replace("http://", "") for host in hosts]

  print "discovered etcd hosts:", ",".join(hosts)

  for index, host in enumerate(hosts):
    server_configuration = SERVER_CONFIGURATION.format(
      name="host-" + str(index), address=host, port=options.port)
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
  parser.add_argument("--port", type=int, default=4001)
  parser.add_argument("--poll-interval", type=int, default=300)
  parser.add_argument("--discovery-url",
    default=os.environ.get("ETCD_DISCOVERY_URL"))
  options = parser.parse_args(args)

  Configure(options)
  proc = subprocess.Popen(["haproxy", "-f", "/haproxy.cfg"])

  while True:
    time.sleep(options.poll_interval)
    state = Configure(options)
    if state is CHANGED:
      proc.send_signal(signal.SIGHUP)

if __name__ == "__main__":
  Main()
