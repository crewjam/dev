

from os.path import join as pathjoin

from dev.units.ambassador import MasterOnlyAmbassadorUnit
from dev.units.data_volume import DataVolumeUnit
from dev.units.docker import ContainerRunnerUnit
from dev.units.presence import PresenceUnit
from dev.units.unit import PodUnit
from dev.units.postgres import PostgresPod

class GerritFrontendPod(PodUnit):
  APP_CONTAINER = "crewjam/gerrit"

  def __init__(self, service_name):
    service_name = service_name or "gerrit"
    PodUnit.__init__(self, service_name=service_name)

    self.app = ContainerRunnerUnit(container=self.APP_CONTAINER,
      name=service_name + "-app")
    self.app.ports.append("8080:8080")
    self.app.ports.append("29418:29418")
    self.AddChild(self.app)

    self.app_presence = PresenceUnit(self.app)
    self.AddChild(self.app_presence, bind=True)

    # TODO(ross): what if we need access to multiple postgres instances? We
    #   should use docker --link instead I think, if we can get it to work
    self.postgres_amb = MasterOnlyAmbassadorUnit(
      foreign_service_name=service_name + "-db",
      local_service_name=service_name,
      port=5432)
    self.AddChild(self.postgres_amb)
    self.app.set("Unit", "After", self.postgres_amb.name + "@%i.service")
    self.app.environment["POSTGRES_SERVER"] = "${COREOS_PRIVATE_IPV4}"
    self.app.environment["SERVICE_NAME"] = service_name

    self.data_volume = DataVolumeUnit(
      volume_name=service_name + "-git",
      name=service_name + "-data-volume-git")
    self.AddChild(self.data_volume)
    self.app.set("Unit", "After", self.data_volume.name + "@%i.service")
    self.app.volumes.append((self.data_volume.host_path, "/data/git"))


class GerritDatabasePod(PostgresPod):
  def __init__(self, service_name=None):
    service_name = service_name or "gerrit"
    PostgresPod.__init__(self, service_name + "-db")


def Build(options, output):
  service_name = "gerrit"
  frontend_pod = GerritFrontendPod(service_name=service_name)
  file(pathjoin(output, frontend_pod.name + "@.service"), "w").write(
    str(frontend_pod))
  for child_unit in frontend_pod.children:
    file(pathjoin(output, child_unit.name + "@.service"), "w").write(
      str(child_unit))

  db_pod = GerritDatabasePod(service_name=service_name)
  file(pathjoin(output, db_pod.name + "@.service"), "w").write(str(db_pod))
  for child_unit in db_pod.children:
    file(pathjoin(output, child_unit.name + "@.service"), "w").write(
      str(child_unit))


if __name__ == "__main__":
  Build(".")
