
import argparse
import sys

from dev.units.docker import ContainerRunnerUnit

class AmbassadorUnit(ContainerRunnerUnit):
  CONTAINER = "crewjam/ambassador"

  def __init__(self, foreign_service_name, local_service_name, port):
    self.port = port
    self.foreign_service_name = foreign_service_name
    self.local_service_name = local_service_name
    self.local_base_service_name = local_service_name.split("@")[0]

    ContainerRunnerUnit.__init__(self,
      container=self.CONTAINER,
      name="{}-{}-amb".format(self.foreign_service_name,
        self.local_base_service_name),
      description="{} ambassador for {}".format(self.foreign_service_name,
        self.local_base_service_name))
    self.options.extend(["-p", "{}:{}".format(self.port, self.port)])

    self.command = [
      "/bin/ambassador",
      "--etcd-prefix=/services/{}".format(self.foreign_service_name),
      "--etcd=${COREOS_PRIVATE_IPV4}",
      "--port={}".format(self.port),
    ]

    self.extra_unit.append("Before={}".format(self.local_service_name))

    self.x_fleet.append("X-ConditionMachineOf={}".format(self.local_service_name))

    # Sadly we cannot run on hosts with any of these other things because we
    # bind to our port just like they do.
    self.x_fleet.append("X-Conflicts={}@*.service".format(
      self.foreign_service_name))


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--foreign-service", "-f")
  parser.add_argument("--local-service", "-l")
  parser.add_argument("--port", "-p", type=int)
  options = parser.parse_args(args)

  unit = AmbassadorUnit(foreign_service_name=options.foreign_service,
    local_service_name=options.local_service, port=options.port)
  print str(unit)


if __name__ == "__main__":
  Main()
