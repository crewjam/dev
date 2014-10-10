

import argparse
import sys

from dev.units.docker import ContainerRunnerUnit


class EtcdAmbassadorUnit(ContainerRunnerUnit):
  def __init__(self, discovery_url):
    ContainerRunnerUnit.__init__(self, "crewjam/etcd-amb")

    self.environment["ETCD_DISCOVERY_URL"] = discovery_url

    # start before fleet
    self.set("Unit", "Before", "fleet.service")

    # start after docker
    self.set("Unit", "After", "docker.service")
    self.set("Unit", "Wants", "docker.service")

    # can't be on the same host as etcd
    self.set("Unit", "Conflicts", "etcd.service")

    self.ports.append("4001:4001")


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--discovery-url")
  options = parser.parse_args(args)

  unit = EtcdAmbassadorUnit(discovery_url=options.discovery_url)
  print str(unit)


if __name__ == "__main__":
  Main()
