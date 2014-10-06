
import argparse
import sys
from os.path import join as pathjoin, dirname

sys.path.insert(0, pathjoin(dirname(dirname(__file__)), "lib"))
from docker_unit import ContainerRunnerUnit


class PresenceUnit(ContainerRunnerUnit):
  CONTAINER = "crewjam/presence"

  def __init__(self, service_name):
    self.service_name = service_name
    self.base_service_name = service_name.split("@")[0]
    ContainerRunnerUnit.__init__(self,
      container=self.CONTAINER,
      name=self.base_service_name + "-presence",
      description=self.base_service_name + " presence")

    self.shell = True
    self.command = [
      "/bin/presence",
      "--etcd-prefix=/services/{}".format(self.base_service_name),
      "--etcd=${COREOS_PRIVATE_IPV4}",
      "--instance=%i",
      "--host=%H",
      "--private-ip=${COREOS_PRIVATE_IPV4}",
      "--public-ip=${COREOS_PUBLIC_IPV4}"
    ]

    self.extra_unit.append("BindsTo={}".format(self.service_name))
    self.x_fleet.append("X-ConditionMachineOf={}".format(self.service_name))


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--service", "-s")
  options = parser.parse_args(args)

  unit = PresenceUnit(service_name=options.service)
  print str(unit)


if __name__ == "__main__":
  Main()
