
import operator
from collections import OrderedDict



class SystemdUnit(object):
  def __init__(self):
    # A dictionary of section -> [(name, value)]
    self._data = OrderedDict()
    self.children = []

  def set(self, section, name, value):
    self._data.setdefault(section, []).append((name, value))

  def replace(self, section, name, value):
    section_items = self._data.setdefault(section, [])
    section_items = [(k, v) for (k, v) in section_items if k != name]
    section_items.append((name, value))

  def remove(self, section, name):
    section_items = self._data.setdefault(section, [])
    section_items = [(k, v) for (k, v) in section_items if k != name]
    self._data[section] = section_items

  def __str__(self):
    lines = []
    for section, section_items in self._data.items():
      lines.append("[{}]".format(section))
      for name, value in section_items:
        if operator.isCallable(value):
          value = value()
        value = str(value)
        lines.append("{}={}".format(name, value))
      lines.append("")
    return "\n".join(lines)

  def AddChild(self, unit, bind=False):
    self.set("Unit", "Requires", unit.name + "@%i.service")
    if bind:
      self.set("Unit", "BindsTo", unit.name + "@%i.service")
    self.children.append(unit)

    unit.set("Unit", "BindsTo", self.name + "@%i.service")
    unit.set("X-Fleet", "X-ConditionMachineOf", self.name + "@%i.service")

class PodUnit(SystemdUnit):
  def __init__(self, service_name):
    SystemdUnit.__init__(self)
    self.service_name = service_name
    self.name = "{}-pod".format(service_name)
    self.set("Service", "ExecStart",
      "/bin/bash -c 'while true; do sleep 10; done")
    self.set("X-Fleet", "X-Conflicts", self.name + "@*.service")


