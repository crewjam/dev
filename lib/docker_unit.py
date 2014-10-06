import StringIO

class ContainerRunnerUnit(object):
  def __init__(self, container, name, description):
    self.container = container
    self.name = name or container
    self.description = description or name
    self.prestart_kill = True
    self.prestart_rm = True
    self.prestart_pull = True
    self.extra_prestart = []
    self.extra_service = []
    self.extra_unit = []
    self.x_fleet = []
    self.options = []
    self.command = []
    self.shell = False

  def GetDockerRunCommand(self):
    options = " ".join(self.options)
    command = " ".join(self.command)
    return_value = "/usr/bin/docker run --rm --name {self.name} " \
      "{options} {self.container} {command}".format(**locals())
    if self.shell:
      return_value = "/bin/bash -c '{}'".format(
        return_value.replace("'", "\\'"))
    return return_value

  def __str__(self):
    unit = StringIO.StringIO()

    print >>unit, "[Unit]"
    print >>unit, "Description=" + self.description
    for extra_unit_line in self.extra_unit:
      print >>unit, extra_unit_line
    print >>unit, ""

    print >>unit, "[Service]"
    print >>unit, "EnvironmentFile=/etc/environment"
    print >>unit, "TimeoutStartSec=0"
    if self.prestart_kill:
      print >>unit, "ExecStartPre=-/usr/bin/docker kill " + self.name
    if self.prestart_rm:
      print >>unit, "ExecStartPre=-/usr/bin/docker rm " + self.name
    if self.prestart_pull:
      print >>unit, "ExecStartPre=/usr/bin/docker pull " + self.container
    for extra_prestart in self.extra_prestart:
      print >>unit, "ExecStartPre=" + extra_prestart
    print >>unit, "ExecStart=" + self.GetDockerRunCommand()
    print >>unit, "ExecStop=/usr/bin/docker kill " + self.name

    for service_line in self.extra_service:
      print >>unit, service_line
    print >>unit, ""

    if self.x_fleet:
      print >>unit, "[X-Fleet]"
      for line in self.x_fleet:
        print >>unit, line

    return unit.getvalue()
