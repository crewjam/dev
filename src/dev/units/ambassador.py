
import argparse
import sys

from dev.units.docker import ContainerRunnerUnit

class AmbassadorUnit(ContainerRunnerUnit):
  CONTAINER = "crewjam/ambassador"

  def __init__(self, foreign_service_name, local_service_name, port):
    self.port = port
    self.foreign_service_name = foreign_service_name
    self.local_service_name = local_service_name

    ContainerRunnerUnit.__init__(self,
      container=self.CONTAINER,
      name="{}-{}-amb".format(self.foreign_service_name,
        self.local_service_name))

    self.ports.append("{}:{}".format(self.port, self.port))

    self.command = self.GetCommand()

  def GetCommand(self):
    return [
      "/bin/ambassador",
      "--etcd-prefix=/services/{}".format(self.foreign_service_name),
      "--etcd=${COREOS_PRIVATE_IPV4}",
      "--port={}".format(self.port),
    ]

class MasterOnlyAmbassadorUnit(AmbassadorUnit):
  def GetCommand(self):
    return AmbassadorUnit.GetCommand(self) + ["--master-only"]


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--foreign-service", "-f", required=True)
  parser.add_argument("--local-service", "-l", required=True)
  parser.add_argument("--port", "-p", type=int, required=True)
  options = parser.parse_args(args)

  unit = AmbassadorUnit(foreign_service_name=options.foreign_service,
    local_service_name=options.local_service, port=options.port)
  print str(unit)


if __name__ == "__main__":
  Main()
