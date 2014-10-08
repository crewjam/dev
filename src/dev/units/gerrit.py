

from os.path import join as pathjoin

from dev.units.ambassador import AmbassadorUnit
from dev.units.btsync import DataVolumeUnit
from dev.units.docker import ContainerRunnerUnit
from dev.units.presence import PresenceUnit


class GerritUnit(ContainerRunnerUnit):
  CONTAINER = "crewjam/gerrit"

  def __init__(self):
    ContainerRunnerUnit.__init__(self,
      container=self.CONTAINER,
      name="gerrit",
      description="gerrit")

    self.shell = True
    self.options.extend([
      '-v', '/var/lib/data/data-volume-gerrit:/data/git',
      '-p', '8080:8080',
      '-p', '29418:29418',
      '-e', 'POSTGRES_SERVER=${COREOS_PRIVATE_IPV4}',
      '-e', 'GERRIT_URL=$(etcdctl get /services/gerrit/url)'
    ])

    self.extra_unit.append("After=gerrit-postgres-ambassador@%i.service")
    self.extra_unit.append("After=gerrit-data-volume@%i.service")

    self.x_fleet.extend([
      "X-Conflicts=gerrit@*.service",
      "X-ConditionMachineOf=gerrit-postgres-ambassador@%i.service",
      "X-ConditionMachineOf=gerrit-data-volume@%i.service",
    ])

class GerritPresenceUnit(PresenceUnit):
  def __init__(self):
    PresenceUnit.__init__(self, "gerrit@%i.service")

class GerritDataVolume(DataVolumeUnit):
  def __init__(self):
    DataVolumeUnit.__init__(self, "gerrit@%i.service")

class GerritPostgresAmbassador(AmbassadorUnit):
  def __init__(self):
    AmbassadorUnit.__init__(self, foreign_service_name="postgres",
      local_service_name="gerrit", port=5432)

def Build(options, output):
  file(pathjoin(output, "gerrit@.service"), "w")\
    .write(str(GerritUnit()))
  file(pathjoin(output, "gerrit-presence@.service"), "w")\
    .write(str(GerritPresenceUnit()))
  file(pathjoin(output, "gerrit-data-volume@.service"), "w")\
    .write(str(GerritDataVolume()))
  file(pathjoin(output, "gerrit-postgres-amb@.service"), "w")\
    .write(str(GerritPostgresAmbassador()))

if __name__ == "__main__":
  Build(".")
