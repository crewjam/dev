

from os.path import join as pathjoin

from dev.units.docker import ContainerRunnerUnit
from dev.units.presence import PresenceUnit

class NginxUnit(ContainerRunnerUnit):
  def __init__(self):
    ContainerRunnerUnit.__init__(self, container="crewjam/nginx", name="nginx")
    self.ports.append("80:80")
    self.ports.append("443:443")
    self.ports.append("1022:1022")

    self.presence_unit = PresenceUnit(self)
    self.AddChild(self.presence_unit, bind=True)


def Build(options, output):
  unit = NginxUnit()
  file(pathjoin(output, unit.name + "@.service"), "w").write(str(unit))
  for child_unit in unit.children:
    file(pathjoin(output, child_unit.name + "@.service"), "w").write(
      str(child_unit))

  dns_unit = ContainerRunnerUnit(container="crewjam/presence-dns",
    name=unit.name + "-presence-dns")
  dns_unit.environment["SERVICE_NAME"] = unit.name

  file(pathjoin(output, dns_unit.name + ".service"), "w").write(str(dns_unit))


if __name__ == "__main__":
  Build(".")
