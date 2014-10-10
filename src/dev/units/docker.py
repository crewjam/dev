
import operator
import pipes
from collections import OrderedDict

from dev.units.unit import SystemdUnit

class ContainerRunnerUnit(SystemdUnit):
  def __init__(self, container, name=None, description=None):
    SystemdUnit.__init__(self)
    self.container = container
    self.name = name if name else container.split("/")[-1]

    self.set("Unit", "Description",
      description if description else lambda: self.name)

    self.set("Service", "EnvironmentFile", "/etc/environment")
    self.set("Service", "TimeoutStartSec", "120")

    self.set("Service", "Restart", "always")
    self.set("Service", "RestartSec", "15sec")
    self.set("Service", "StartLimitInterval", "10")
    self.set("Service", "StartLimitBurst", "5")

    self.set("Service", "ExecStartPre",
      lambda: "-/usr/bin/docker kill {}".format(self.name))
    self.set("Service", "ExecStartPre",
      lambda: "-/usr/bin/docker rm {}".format(self.name))
    self.set("Service", "ExecStartPre",
      lambda: "-/usr/bin/docker pull {}".format(self.container))
    self.set("Service", "ExecStart", self.GetDockerRunCommand)
    self.set("Service", "ExecStop",
      lambda: "/usr/bin/docker kill {}".format(self.name))

    self.environment = OrderedDict()
    self.environment["INSTANCE"] = "%i"
    self.environment["HOSTNAME"] = "%H"
    self.environment["PUBLIC_IP"] = "${COREOS_PUBLIC_IPV4}"
    self.environment["PRIVATE_IP"] = "${COREOS_PRIVATE_IPV4}"
    self.environment["ETCDCTL_PEERS"] = "http://${COREOS_PRIVATE_IPV4}:4001"

    self.ports = []
    self.volumes = []
    self.command = []

  def GetDockerRunCommand(self):
    command = ["/usr/bin/docker", "run", "--rm"]
    command.extend(["--name", self.name])
    for name, value in self.environment.items():
      if operator.isCallable(value):
        value = value()
      command.extend(["-e", "{}={}".format(name, value)])
    for value in self.ports:
      if operator.isCallable(value):
        value = value()
      command.extend(["-p", str(value)])
    for value in self.volumes:
      if operator.isCallable(value):
        value = value()
      if isinstance(value, tuple):
        host_path, container_path = value
        value = host_path + ":" + container_path
      command.extend(["-v", str(value)])
    command.append(self.container)
    if self.command:
      command.extend(self.command)
    return " ".join(map(pipes.quote, command))
