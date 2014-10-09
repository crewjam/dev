
import argparse
import sys

from dev.units.docker import ContainerRunnerUnit


class DataVolumeUnit(ContainerRunnerUnit):
  CONTAINER = "crewjam/btsync"

  def __init__(self, volume_name, name=None):
    ContainerRunnerUnit.__init__(self,
      container=self.CONTAINER,
      name=name or "data-volume-{}".format(volume_name),
      description="btsync data volume {}".format(volume_name))

    self.host_path = "/data0/{}".format(self.name)
    self.volumes.append(lambda: "{}:/data".format(self.host_path))
    self.environment["VOLUME_NAME"] = volume_name

    # We rely on having etcd available either via etcd or etcd-amb
    self.environment["ETCDCTL_PEERS"] = "http://${COREOS_PRIVATE_IPV4}:4001"
    self.set("Unit", "After", "etcd-amb.service")
    self.set("Unit", "After", "etcd.service")

def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  parser.add_argument("--volume", "-v")
  options = parser.parse_args(args)

  unit = DataVolumeUnit(volume_name=options.volume)
  print str(unit)


if __name__ == "__main__":
  Main()
