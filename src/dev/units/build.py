import argparse
import sys
from os.path import join as pathjoin

from dev.units.ambassador import AmbassadorUnit
from dev.units.btsync import DataVolumeUnit
from dev.units.docker import ContainerRunnerUnit
from dev.units.elasticsearch import ElasticsearchPresenceUnit, \
  ElasticsearchAmbassadorUnit, ElasticsearchUnit
from dev.units.etcd import EtcdAmbassadorUnit
from dev.units.presence import PresenceUnit
from dev.units.gerrit import Build

def BuildUnits(options, output):
  Build(options, output)

def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--discovery-url")
  parser.add_argument("--output", default=".")
  options = parser.parse_args(args)

  BuildUnits(options, options.output)

if __name__ == "__main__":
  Main()