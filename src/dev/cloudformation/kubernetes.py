
import textwrap

from dev.cloudformation.nodes import NodeBuilder
from dev.units.etcd import EtcdAmbassadorUnit

FLANNEL_SERVICE = textwrap.dedent("""
  [Unit]
  After=network-online.target
  Wants=network-online.target
  Description=flannel is an etcd backed overlay network for containers

  [Service]
  ExecStartPre=-/usr/bin/mkdir -p /opt/bin
  ExecStartPre=/usr/bin/wget -N -P /opt/bin http://storage.googleapis.com/flannel/flanneld
  ExecStartPre=/usr/bin/chmod +x /opt/bin/flanneld
  ExecStartPre=/bin/bash -c '\
    e="etcdctl -peers http://{discovery_slug}.etcd.ctudev.com:4001" ; \
    while ! $e get /coreos.com/network/config ; do \
      sleep 5; \
      $e mk /coreos.com/network/config "{{\\\\"Network\\\\":\\\\"172.16.0.0/16\\\\"}}" ; \
    done'
  ExecStart=/opt/bin/flanneld -etcd-endpoint http://{discovery_slug}.etcd.ctudev.com:4001
  Restart=always
  """)

DOCKER_SERVICE = textwrap.dedent("""
  [Unit]
  After=flannel.service
  Wants=flannel.service
  Description=Docker Application Container Engine
  Documentation=http://docs.docker.io

  [Service]
  EnvironmentFile=/run/flannel/subnet.env
  ExecStartPre=/usr/bin/mount --make-rprivate /
  ExecStart=/usr/bin/docker -d --bip=${FLANNEL_SUBNET} --mtu=${FLANNEL_MTU} -s=btrfs
  Restart=always

  [Install]
  WantedBy=multi-user.target
  """)

SETUP_NETWORK_ENVIRONMENT_SERVICE = textwrap.dedent("""
  [Unit]
  Description=Setup Network Environment
  Documentation=https://github.com/kelseyhightower/setup-network-environment
  Requires=network-online.target
  After=network-online.target

  [Service]
  ExecStartPre=-/usr/bin/mkdir -p /opt/bin
  ExecStartPre=/usr/bin/wget -N -P /opt/bin http://storage.googleapis.com/snenv/setup-network-environment
  ExecStartPre=/usr/bin/chmod +x /opt/bin/setup-network-environment
  ExecStart=/opt/bin/setup-network-environment
  RemainAfterExit=yes
  Type=oneshot
  """)

class KubernetesNodeBuilder(NodeBuilder):
  name = "kubernetes"
  instance_type = "m3.medium"

  def BuildCloudConfigYaml(self):
    discovery_slug = self.options.discovery_url.split("/")[-1]
    data = {
      "coreos": {
        "fleet": {
          "metadata": "role=kubernetes"
        },
        "units": [
          {"name": "fleet.service", "command": "start"},
          {"name": "etcd.service", "command": "stop"},
          {"name": "etcd-amb.service", "command": "start", "content":
            str(EtcdAmbassadorUnit(discovery_url=self.options.discovery_url))},
          {"name": "flannel.service", "command": "start",
            "content": FLANNEL_SERVICE.format(discovery_slug=discovery_slug)},
          {"name": "docker.service", "command": "start",
            "content": DOCKER_SERVICE},
          {"name": "setup-network-environment.service", "command": "start",
            "content": SETUP_NETWORK_ENVIRONMENT_SERVICE},
        ]
      }
    }
    return data

  def AuthorizeServices(self):
    self.AuthorizeInternalService("flannel" + str(8285), 8285, "kubernetes", "udp")
    self.AuthorizeInternalService("kubernetes" + str(10250), 10250, "kubernetes")
    self.AuthorizeInternalService("kubernetes" + str(8080), 8080, "kubernetes")

  def GetAutoScaleSizeLimits(self):
    min_size, max_size = 0, 9
    return min_size, max_size