
import argparse
import sys
from os.path import join as pathjoin, dirname

sys.path.insert(0, pathjoin(dirname(dirname(__file__)), "lib"))
from docker_unit import ContainerRunnerUnit


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

    self.command = [
      "/bin/ambassador",
      "--etcd-prefix=/services/{}".format(self.foreign_service_name),
      "--etcd=${COREOS_PRIVATE_IPV4}",
      "--port={}".format(self.port),
    ]

    self.extra_unit.append("Before={}".format(self.service_name))
    self.x_fleet.append("X-ConditionMachineOf={}".format(self.service_name))


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--foreign-service", "-f")
  parser.add_argument("--local-service", "-l")
  parser.add_argument("--port", type=int)
  options = parser.parse_args(args)

  unit = AmbassadorUnit(foreign_service_name=options.foreign_service,
    local_service_name=options.local_service, port=options.port)
  print str(unit)


if __name__ == "__main__":
  Main()
