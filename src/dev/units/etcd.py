

import argparse
import sys

from dev.units.docker import ContainerRunnerUnit


class EtcdAmbassadorUnit(ContainerRunnerUnit):
  CONTAINER = "crewjam/etcd-amb"

  def __init__(self, discovery_url):
    ContainerRunnerUnit.__init__(self,
      container=self.CONTAINER,
      name="etcd-amb",
      description="etcd ambassador")
    self.options.extend(["-e", "ETCD_DISCOVERY_URL=" + discovery_url])

    # start before fleet
    self.extra_unit.append("Before=fleet.service")

    # start after docker
    self.extra_unit.extend([
      "After=docker.service",
      "Wants=docker.service",
    ])

    self.extra_service.append("Restart=always")

    # can't be on the same host as etcd
    self.extra_unit.append("Conflicts=etcd.service")

    self.options.extend(["-p", "4001:4001"])


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--discovery-url")
  options = parser.parse_args(args)

  unit = EtcdAmbassadorUnit(discovery_url=options.discovery_url)
  print str(unit)


if __name__ == "__main__":
  Main()
