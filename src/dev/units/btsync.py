
import argparse
import sys

from dev.units.docker import ContainerRunnerUnit


class DataVolumeUnit(ContainerRunnerUnit):
  CONTAINER = "crewjam/btsync"

  def __init__(self, service_name):
    self.service_name = service_name
    ContainerRunnerUnit.__init__(self,
      container=self.CONTAINER,
      name="data-volume",
      description="btsync data volume")

    self.options.extend(["-v", "/var/lib/data/%p:/data"])
    self.shell = True
    self.command = [
      "/main",
      "$(/usr/bin/etcdctl get /services/%p/btsync_secret)"
    ]

    # Generate a secret if one is not present in etcd
    self.extra_prestart.append("/bin/bash -ex -c '\
      /usr/bin/etcdctl get /services/%p/btsync_secret || (\
        /usr/bin/docker run crewjam/btsync btsync --generate-secret | \
          /usr/bin/etcdctl mk /services/%p/btsync_secret;\
        sleep 10;\
      )'")

    self.extra_unit.append("Before={}".format(self.service_name))
    self.x_fleet.append("X-ConditionMachineOf={}".format(self.service_name))


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--service", "-s")
  options = parser.parse_args(args)

  unit = DataVolumeUnit(service_name=options.service)
  print str(unit)


if __name__ == "__main__":
  Main()
