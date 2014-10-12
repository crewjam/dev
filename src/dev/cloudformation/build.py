
import argparse
import json
import re
import sys
import urllib2

import boto
import boto.cloudformation

from dev.cloudformation.network import BuildNetwork
from dev.cloudformation.nodes import MainNodeBuilder, WorkerNodeBuilder
from dev.cloudformation.elasticsearch import ElasticsearchNodeBuilder
from dev.cloudformation.kubernetes import KubernetesNodeBuilder
from dev.cloudformation.chaosmonkey import BuildChaosMonkey

data = {
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "CoreOS",
  "Parameters": {
    "KeyPair" : {
      "Description" : "The name of an EC2 Key Pair to allow SSH access to the instance.",
      "Type" : "String"
    },
  },
  "Mappings": {
    "RegionMap" : {
      # TODO(ross): remove this map because we know the region at compile time
      # TODO(ross): these AMIs use EBS, we would prefer instance store.
      # TODO(ross): figure out how to keep this map up to date
      "us-west-2" : {
          "AMI" : "ami-e790ddd7",  # beta channel
      },
    }
  },
  "Resources": {}
}

def Build(options, data):
  BuildNetwork(options, data)
  MainNodeBuilder(options, data)()
  WorkerNodeBuilder(options, data)()
  KubernetesNodeBuilder(options, data)()
  #ElasticsearchNodeBuilder(options, data)()
  BuildChaosMonkey(options, data)

def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("mode", choices=["cat", "validate", "create", "update"])
  parser.add_argument("--dns-name", required=True)
  parser.add_argument("--discovery-url")
  #parser.add_argument("--with-elasticsearch", action="store_true")
  parser.add_argument("--key", required=True)
  options = parser.parse_args(args)

  if not options.discovery_url:
    options.discovery_url = \
      urllib2.urlopen("https://discovery.etcd.io/new").read().strip()
    print "discovery_url:", options.discovery_url

  stack_name = re.sub("[^a-z0-9]", "", options.dns_name)
  print "stack_name:", stack_name

  Build(options, data)

  if options.mode == "cat":
    print json.dumps(data, indent=2)
    return

  cf = boto.cloudformation.connect_to_region("us-west-2")
  if options.mode == "validate":
    cf.validate_template(template_body=json.dumps(data))
    return

  if options.mode == "create":
    cf.create_stack(stack_name, template_body=json.dumps(data),
      parameters=[("KeyPair", options.key)],
      capabilities=['CAPABILITY_IAM'])
    return

  if options.mode == "update":
    cf.update_stack(stack_name, template_body=json.dumps(data),
      parameters=[("KeyPair", options.key)],
      capabilities=['CAPABILITY_IAM'])
    return


if __name__ == "__main__":
  Main()

