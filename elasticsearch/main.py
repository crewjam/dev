#!/usr/bin/python -u

import argparse
import sys
import os
import uuid
from os.path import isdir

import etcd

def GetCommand(options, client):
  command = [
    "/elasticsearch/bin/elasticsearch"
  ]

  command.append("-Des.node.master=" + str(options.master_node).lower())
  command.append("-Des.node.data=" + str(options.data_node).lower())
  if options.node_name:
    command.append("-Des.node.name=" + options.node_name)

  if options.publish_host:
    command.append("-Des.network.publish_host=" + options.publish_host)

  # Set or create cluster name
  try:
    command.append("-Des.cluster.name=" +
      client.get(options.etcd_prefix + "/cluster_name").value)
  except KeyError:
    print "setting cluster name"
    client.write(options.etcd_prefix + "/cluster_name", str(uuid.uuid4()),
      prevExist=False)
    command.append("-Des.cluster.name=" +
      client.get(options.etcd_prefix + "/cluster_name").value)

  peers = []
  try:
    instance_keys = client.get(options.etcd_prefix + "/master/instances/").children
  except KeyError:
    return None

  for instance_key in instance_keys:
    try:
      address = client.get(instance_key.key + "/private_ip").value
    except KeyError:
      continue
    peers.append(address)

  if not peers:
    print "no peers could be found"
    return None
  command.append("-Des.discovery.zen.ping.unicast.hosts=" + " ".join(peers))

  data_dirs = []
  for index in range(10):
    if isdir("/data{}".format(index)):
      data_dirs.append("/data{}".format(index))
  if data_dirs:
    command.append("-Des.path.data=" + ",".join(data_dirs))

  print " ".join(command)
  return command

def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--etcd", default="localhost")
  parser.add_argument("--etcd-prefix", default="/services/elasticsearch")
  parser.add_argument("--node-name")
  parser.add_argument("--master-node", action="store_true")
  parser.add_argument("--data-node", action="store_true")
  parser.add_argument("--publish-host")

  options = parser.parse_args(args)

  client = etcd.Client(host=options.etcd)

  while True:
    command = GetCommand(options, client=client)
    if command:
      break
    client.read(options.etcd_prefix, recursive=True, wait=True, waitIndex=0)
  os.execv(command[0], command)


if __name__ == "__main__":
  Main()
