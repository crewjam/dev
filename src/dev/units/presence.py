
import argparse
import sys
from os.path import join as pathjoin, dirname

from dev.units.docker import ContainerRunnerUnit


class PresenceUnit(ContainerRunnerUnit):
  CONTAINER = "crewjam/presence"

  def __init__(self, unit):
    name = unit.name + "-presence"
    ContainerRunnerUnit.__init__(self, container=self.CONTAINER, name=name)

    self.environment["SERVICE_NAME"] = unit.name

    self.set("Unit", "After", "{}@%i.service".format(unit.name))
    self.set("Unit", "BindsTo", "{}@%i.service".format(unit.name))
    self.set("X-Fleet", "X-ConditionMachineOf",
      "{}@%i.service".format(unit.name))


def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--service", "-s")
  options = parser.parse_args(args)

  unit = PresenceUnit(service_name=options.service)
  print str(unit)


if __name__ == "__main__":
  Main()
