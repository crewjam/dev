
import sys
from os.path import join as pathjoin, dirname

sys.path.insert(0, pathjoin(dirname(dirname(__file__)), "lib"))
from docker_unit import ContainerRunnerUnit
from nodes import NodeBuilder, EtcdAmbassadorUnit

class ElasticsearchPresenceUnit(ContainerRunnerUnit):
  def __init__(self, master=True, data=True):
    type_name = {
      (True, True): "node",
      (True, False): "master",
      (False, True): "data",
      (False, False): "client"
    }[(master, data)]

    ContainerRunnerUnit.__init__(self,
      container="crewjam/presence",
      name="elasticsearch-" + type_name + "-presence",
      description="elasticsearch presence")

    self.extra_unit.append("BindsTo=elasticsearch-{}@%i.service".format(type_name))
    self.command = [
      "/bin/presence",
      "--etcd-prefix=/services/elasticsearch/{}".format(type_name),
      "--etcd=${COREOS_PRIVATE_IPV4}",
      "--instance=%i",
      "--host=$(hostname)",
      "--private-ip=${COREOS_PRIVATE_IPV4}"
    ]

    self.x_fleet.append("X-ConditionMachineOf=elasticsearch-{}@%i.service"
      .format(type_name))

class ElasticsearchAmbassadorUnit(ContainerRunnerUnit):
  def __init__(self, service_name):
    self.service_name = service_name
    self.base_service_name = service_name.split("@")[0]

    ContainerRunnerUnit.__init__(self,
      container="crewjam/ambassador",
      name="elasticsearch-{}-amb".format(self.base_service_name),
      description="Elasticsearch ambassador for {}".format(self.base_service_name))
    self.options.extend(["-p", "9200:9200"])
    self.command = [
      "/bin/ambassador",
      "--etcd-prefix=/services/elasticsearch/client",
      "--etcd=${COREOS_PRIVATE_IPV4}",
      "--port=9200"
    ]

    self.extra_unit.append("Before={}".format(self.service_name))

    self.x_fleet.append("X-ConditionMachineOf={}".format(self.service_name))

    # Sadly we cannot run on hosts with any of these other things because we
    # bind to port 9200 just like they do.
    self.x_fleet.extend([
      "X-Conflicts=elasticsearch-client@*.service",
      "X-Conflicts=elasticsearch-data@*.service",
      "X-Conflicts=elasticsearch-master@*.service",
    ])

class ElasticsearchUnit(ContainerRunnerUnit):
  def __init__(self, master=True, data=True):
    type_name = {
      (True, True): "node",
      (True, False): "master",
      (False, True): "data",
      (False, False): "client"
    }[(master, data)]

    ContainerRunnerUnit.__init__(self,
      container="crewjam/elasticsearch",
      name="elasticsearch-" + type_name,
      description="elasticsearch container")

    self.extra_service.append("EnvironmentFile=/etc/environment")

    self.command = [
      "/main",
      "--etcd=${COREOS_PRIVATE_IPV4}",
      "--publish-host=${COREOS_PRIVATE_IPV4}",
      "--node-name=%H",
    ]
    if master:
      self.command.append("--master-node")
    if data:
      self.command.append("--data-node")

    self.options.extend(["-p", "9200:9200"])
    self.options.extend(["-p", "9300:9300"])
    if data:
      self.options.extend(["-v", "/data0:/data0"])
      self.options.extend(["-v", "/data1:/data1"])

    for type_name_ in ["node", "master", "data", "client"]:
      self.x_fleet.append("X-Conflicts=elasticsearch-{}@*.service"
        .format(type_name_))

class ElasticsearchNodeBuilder(NodeBuilder):
  name = "nodes-es"
  instance_type = "m3.xlarge"

  def BuildCloudConfigYaml(self):
    data = {
      "coreos": {
        "fleet": {
          "metadata": "role=main"
        },
        "units": [
          {"name": "etcd-amb.service", "command": "start", "content":
            str(EtcdAmbassadorUnit(discovery_url=self.options.discovery_url))},
          {"name": "elasticsearch.service", "command": "start", "content":
            str(ElasticsearchUnit(master=False, data=True))},
          {
            "name": "data0.mount",
            "command": "start",
            "content":
              "[Mount]\n"
              "What=/dev/xvdb\n"
              "Where=/data0\n"
              "Type=ext3\n"
          },
          {
            "name": "data1.mount",
            "command": "start",
            "content":
              "[Mount]\n"
              "What=/dev/xvdc\n"
              "Where=/data1\n"
              "Type=ext3\n"
          }
        ]
      }
    }
    return data

  def AuthorizeServices(self):
    for group in ["nodes-main", "nodes-es", "nodes-worker"]:
      for port in [9200, 9300]:
        self.AuthorizeInternalService("elasticsearch" + str(port), port, group)

  def GetAutoScaleSizeLimits(self):
    min_size, max_size = 3, 30
    return min_size, max_size

if __name__ == "__main__":
  file("elasticsearch-master@.service", "w").write(
    str(ElasticsearchUnit(master=True, data=False)))
  file("elasticsearch-master-presence@.service", "w").write(
    str(ElasticsearchPresenceUnit(master=True, data=False)))
  file("elasticsearch-client@.service", "w").write(
    str(ElasticsearchUnit(master=False, data=False)))
  file("elasticsearch-client-presence@.service", "w").write(
    str(ElasticsearchPresenceUnit(master=False, data=False)))
  file("elasticsearch-data@.service", "w").write(
    str(ElasticsearchUnit(master=False, data=True)))
  file("elasticsearch-data-presence@.service", "w").write(
    str(ElasticsearchPresenceUnit(master=False, data=True)))

  # ambassadors
  for service_name in ["loadtest@%i.service"]:
    base_service_name, suffix = service_name.split("@", 1)
    suffix = suffix.replace("%i", "")
    file("elasticsearch-{}-amb@{}".format(base_service_name, suffix), "w").write(
      str(ElasticsearchAmbassadorUnit(service_name=service_name)))
