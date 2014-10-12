#!/usr/bin/python -u

import argparse
import os
import re
import signal
import subprocess
import sys
from os.path import isfile

import etcd
import urllib3
from jinja2 import Environment, FileSystemLoader

NOP, HUP, RESTART = object(), object(), object()

def Configure(options, client):
  kwargs = {}

  # generic stuff from the service key
  service_key = client.get("/services/{}".format(options.service_name))
  for child_key in service_key.children:
    name = child_key.key.split("/")[-1]
    kwargs[name] = child_key.value

  def GetInstances(service_name):
    items = []
    for instance_key in client.get("/services/{}/instances".format
        (service_name)).children:
      item = {}
      for instance_child_key in client.get(instance_key.key).children:
        name = instance_child_key.key.split("/")[-1]
        item[str(name)] = str(instance_child_key.value)
      if item:
        items.append((instance_key.key, item))
    items.sort()
    items = [v for (k, v) in items]
    return items
  kwargs["GetInstances"] = GetInstances

  env = Environment(loader=FileSystemLoader("/etc/nginx"))
  template = env.get_template("nginx.conf.tmpl")
  conf = template.render(**kwargs)

  action = NOP
  if not isfile("/etc/nginx/nginx.conf") or \
      file("/etc/nginx/nginx.conf").read() != conf:
    file("/etc/nginx/nginx.conf", "w").write(conf)
    action = HUP

  ssl_key = client.get("/services/{}/ssl_key".format(options.service_name))\
    .value
  if not isfile("/etc/nginx/ssl.key") or \
      file("/etc/nginx/ssl.key").read() != ssl_key:
    file("/etc/nginx/ssl.key", "w").write(ssl_key)
    action = RESTART

  ssl_cert = client.get("/services/{}/ssl_cert".format(options.service_name))\
    .value
  if not isfile("/etc/nginx/ssl.crt") or \
      file("/etc/nginx/ssl.crt").read() != ssl_cert:
    file("/etc/nginx/ssl.crt", "w").write(ssl_cert)
    action = RESTART

  return action


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--etcd")
  parser.add_argument("--service-name", default="nginx")
  options = parser.parse_args(args)

  if options.etcd is None:
    options.etcd, = re.match("http://(.*):4001",
      os.environ.get("ETCDCTL_PEERS")).groups()

  client = etcd.Client(host=options.etcd)

  Configure(options, client=client)
  command = ["nginx", "-c", "/etc/nginx/nginx.conf", "-g", "daemon off;"]
  proc = subprocess.Popen(command)

  while True:
    # TODO(ross): make sure proc is still running

    try:
      client.read("/", recursive=True, wait=True, waitIndex=0)
    except urllib3.exceptions.ReadTimeoutError:
      pass

    action = Configure(options, client=client)
    if action is NOP:
      continue

    if action is HUP:
      proc.send_signal(signal.SIGHUP)

    if action is RESTART:
      proc.terminate()
      proc = subprocess.Popen(command)


if __name__ == "__main__":
  Main()
