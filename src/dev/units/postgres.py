

from os.path import join as pathjoin

from dev.units.data_volume import DataVolumeUnit
from dev.units.docker import ContainerRunnerUnit
from dev.units.unit import PodUnit

class PostgresPod(PodUnit):
  APP_CONTAINER = "crewjam/postgres"

  def __init__(self, name):
    PodUnit.__init__(self, service_name=name)

    self.app = ContainerRunnerUnit(container=self.APP_CONTAINER,
      name=name)
    self.app.ports.append("${COREOS_PRIVATE_IPV4}:5432:5432")
    self.app.environment["SERVICE_NAME"] = name
    self.app.environment["INSTANCE"] = "%i"
    self.app.environment["PRIVATE_IP"] = "${COREOS_PRIVATE_IPV4}"

    # We rely on having etcd available either via etcd or etcd-amb
    self.app.environment["ETCDCTL_PEERS"] = "http://${COREOS_PRIVATE_IPV4}:4001"
    self.app.set("Unit", "After", "etcd-amb.service")
    self.app.set("Unit", "After", "etcd.service")
    self.AddChild(self.app)

    self.data_volume = DataVolumeUnit(
      volume_name=name,
      name=name + "-data-volume")
    self.AddChild(self.data_volume)
    self.app.set("Unit", "After", self.data_volume.name + "@%i.service")
    self.app.volumes.append((self.data_volume.host_path,
      "/var/lib/postgresql/data"))


def Build(options, output):
  pod = PostgresPod()
  file(pathjoin(output, pod.name + "@.service"), "w").write(str(pod))
  for child_unit in pod.children:
    file(pathjoin(output, child_unit.name + "@.service"), "w").write(
      str(child_unit))

if __name__ == "__main__":
  Build(".")
