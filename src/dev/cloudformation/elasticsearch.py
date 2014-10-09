
from dev.cloudformation.nodes import NodeBuilder
from dev.units.elasticsearch import ElasticsearchUnit
from dev.units.etcd import EtcdAmbassadorUnit


class ElasticsearchNodeBuilder(NodeBuilder):
  name = "elasticsearch"
  instance_type = "m3.xlarge"

  def BuildCloudConfigYaml(self):
    data = {
      "coreos": {
        "fleet": {
          "metadata": "role=main"
        },
        "units": [
          {"name": "fleet.service", "command": "stop"},
          {"name": "etcd.service", "command": "stop"},
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
    for group in ["main", "elasticsearch", "worker"]:
      for port in [9200, 9300]:
        self.AuthorizeInternalService("elasticsearch" + str(port), port, group)

  def GetAutoScaleSizeLimits(self):
    min_size, max_size = 0, 30
    return min_size, max_size
