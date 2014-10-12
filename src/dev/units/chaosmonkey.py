

from os.path import join as pathjoin

from dev.units.docker import ContainerRunnerUnit
from dev.units.presence import PresenceUnit

class ChoasMonkeyUnit(ContainerRunnerUnit):
  def __init__(self):
    ContainerRunnerUnit.__init__(self, container="crewjam/chaosmonkey",
      name="chaosmonkey")

    self.presence_unit = PresenceUnit(self)
    self.AddChild(self.presence_unit, bind=True)


def Build(options, output):
  unit = ChoasMonkeyUnit()
  file(pathjoin(output, unit.name + "@service"), "w").write(str(unit))
  file(pathjoin(output, unit.presence_unit.name + "@service"), "w").write(
    str(unit.presence_unit))


if __name__ == "__main__":
  Build(".")
