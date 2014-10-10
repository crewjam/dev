import re

import yaml

from dev.units.etcd import EtcdAmbassadorUnit


ZONES = ["us-west-2a", "us-west-2b", "us-west-2c"]


def AWSSafeString(name):
  """
  Returns a version of name that is likely to meet AWS requirements for the
  names of AWS resources.
  """
  return re.sub("[^A-Za-z0-9]", "", name.title())


class NodeBuilder(object):
  """
  Builds an autoscaling group for a class of nodes. This is a base class
  implemented by MainNodeBuilder and WorkerNodeBuilder, etc.
  """
  #: name of the node group
  name = NotImplemented

  #: i.e. m3.medium
  instance_type = NotImplemented

  #: ports allowed from all addresses
  public_ports = [22, 80, 443, 1022]

  def __init__(self, options, data):
    self.options = options
    self.data = data

  def __call__(self):
    self.BuildAutoScalingGroup()
    self.BuildLaunchConfiguration()
    self.BuildSecurityGroup()
    self.AuthorizeServices()
    return self.data

  def GetAutoScaleSizeLimits(self):
    """
    Returns a tuple of (min_size, max_size) for the autoscaling group. The group
    starts at min_size.
    """
    min_size, max_size = 3, 20
    return min_size, max_size

  def BuildAutoScalingGroup(self):
    min_size, max_size = self.GetAutoScaleSizeLimits()

    self.data["Resources"]["AutoScalingGroup" + AWSSafeString(self.name)] = {
        "Type": "AWS::AutoScaling::AutoScalingGroup",
        "Properties": {
          "AvailabilityZones": ZONES,
          "Cooldown": "300",
          "DesiredCapacity": str(min_size),
          "MaxSize": str(max_size),
          "MinSize": str(min_size),
          "HealthCheckGracePeriod": "300",
          "HealthCheckType": "EC2",
          "VPCZoneIdentifier":
            [{"Ref": "VpcSubnet" + AWSSafeString(az)} for az in ZONES],
          "LaunchConfigurationName":
            {"Ref": "LaunchConfiguration" + AWSSafeString(self.name)},
          "Tags": [
            {
              "Key": "Name",
              "Value": "{}/{}".format(self.options.dns_name, self.name),
              "PropagateAtLaunch": True,
            }
          ]
        }
      }

  def BuildUserData(self):
    """
    Returns the user data as a string.
    """
    return "#cloud-config\n" + yaml.dump(self.BuildCloudConfigYaml())

  def BuildCloudConfigYaml(self):
    raise NotImplementedError()

  def BuildLaunchConfiguration(self):
    self.data["Resources"]["LaunchConfiguration" + AWSSafeString(self.name)] = {
      "Type": "AWS::AutoScaling::LaunchConfiguration",
      "DependsOn": "VpcInternetGatewayAttachment",
      "Properties": {
        # TODO(ross): this is not needed because we know which region we are in
        #   at compile time.
        "ImageId": { "Fn::FindInMap" : [ "RegionMap", { "Ref" : "AWS::Region" }, "AMI" ]},
        "InstanceType": self.instance_type,
        "KeyName": {"Ref": "KeyPair"},
        "SecurityGroups": [{"Ref": "SecurityGroup" + AWSSafeString(self.name)}],
        "AssociatePublicIpAddress": "true",
        "BlockDeviceMappings": [
          {"DeviceName": "/dev/sda", "Ebs": {"VolumeSize": 8}},
          {"DeviceName": "/dev/sdb", "VirtualName": "ephemeral0"},
          {"DeviceName": "/dev/sdc", "VirtualName": "ephemeral1"},
        ],
        "UserData": self.BuildUserData().encode("base64"),
      }
    }

  def BuildSecurityGroup(self):
    self.data["Resources"]["SecurityGroup" + AWSSafeString(self.name)] = {
      "Type": "AWS::EC2::SecurityGroup",
      "Properties": {
        "GroupDescription": self.options.dns_name + "/" + self.name,
        "VpcId": {"Ref": "Vpc"},
        "SecurityGroupIngress": [
          # TODO(ross): fix this bad style
          {
            "IpProtocol": "tcp",
            "FromPort": str(port),
            "ToPort": str(port),
            "CidrIp": "0.0.0.0/0"
          } for port in self.public_ports
        ],
        "SecurityGroupEgress": [
          {
            "IpProtocol": "-1",
            "CidrIp": "0.0.0.0/0"
          }
        ]
      }
    }

  def AuthorizeServices(self):
    raise NotImplementedError()

  def AuthorizeInternalService(self, service_name, port, other_group,
      ip_protocol="tcp"):
    sg_name = AWSSafeString("SecurityGroupAllow {} {} to {}".format(
        service_name, other_group, self.name))

    self.data["Resources"][sg_name] = {
      "Type": "AWS::EC2::SecurityGroupIngress",
      "Properties": {
        "GroupId": {"Ref": "SecurityGroup" + AWSSafeString(self.name)},
        "IpProtocol": ip_protocol,
        "FromPort": str(port),
        "ToPort": str(port),
        "SourceSecurityGroupId":
          {"Ref": "SecurityGroup" + AWSSafeString(other_group)}
      }
    }

class MainNodeBuilder(NodeBuilder):
  name = "main"
  instance_type = "m3.medium" # "m1.small"

  def BuildCloudConfigYaml(self):
    data = {
      "coreos": {
        "fleet": {
          "metadata": "role=main"
        },
        "etcd": {
          "discovery": self.options.discovery_url,
          "addr": "$private_ipv4:4001",
          "peer-addr": "$private_ipv4:7001",
        },
        "units": [
          {"name": "etcd.service", "command": "start"},
          {"name": "fleet.service", "command": "start"},
        ]
      }
    }
    return data

  def AuthorizeServices(self):
    # TODO(ross): this is less general than it should be w/r/t allowing
    #   applications
    all_groups = ["main", "worker", "kubernetes"]

    for group in all_groups:
      for port in [4001, 7001]:
        self.AuthorizeInternalService("etcd" + str(port), port, group)
      for port in [5432]:
        self.AuthorizeInternalService("postgres" + str(port), port, group)
      for port in [8080]:
        self.AuthorizeInternalService("http" + str(port), port, group)

  def GetAutoScaleSizeLimits(self):
    min_size, max_size = 1, 3
    return min_size, max_size


class WorkerNodeBuilder(NodeBuilder):
  name = "worker"
  instance_type = "m3.medium"

  def BuildCloudConfigYaml(self):
    data = {
      "coreos": {
        "fleet": {
          "metadata": "role=worker"
        },
        "units": [
          {"name": "fleet.service", "command": "start"},
          {"name": "etcd.service", "command": "stop"},
          {"name": "etcd-amb.service", "command": "start", "content":
            str(EtcdAmbassadorUnit(discovery_url=self.options.discovery_url))}
        ]
      }
    }
    return data

  def AuthorizeServices(self):
    all_groups = ["main", "worker", "kubernetes"]

    for group in all_groups:
      for port in [5432]:
        self.AuthorizeInternalService("postgres" + str(port), port, group)
      for port in [8080]:
        self.AuthorizeInternalService("http" + str(port), port, group)

  def GetAutoScaleSizeLimits(self):
    min_size, max_size = 3, 30
    return min_size, max_size
