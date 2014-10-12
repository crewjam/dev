import re
from dev.cloudformation.util import AWSSafeString

VPC_CIDR_BLOCK = "10.10.0.0/16"
ZONES = ["us-west-2a", "us-west-2b", "us-west-2c"]
SUBNET_CIDR_BLOCKS = ["10.10.0.0/18", "10.10.64.0/18", "10.10.128.0/18",
  "10.10.192.0/18"]


def BuildNetwork(options, data):
  """
  Fill in data with network configuration based on `options`.
  """

  # ---- VPC -------------------------------------------------------------------
  # A VPC with one subnet for each availability zone

  data["Resources"]["Vpc"] = {
    "Type": "AWS::EC2::VPC",
    "Properties": {
      "CidrBlock": VPC_CIDR_BLOCK,
      "InstanceTenancy": "default",
      "EnableDnsSupport": "true",
      "EnableDnsHostnames": "true",
      "Tags": [
        {"Key": "Name", "Value": options.dns_name},
      ]
    }
  }

  for az, cidr_block in zip(ZONES, SUBNET_CIDR_BLOCKS):
    data["Resources"]["VpcSubnet" + AWSSafeString(az)] = {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "CidrBlock": cidr_block,
        "AvailabilityZone": az,
        "VpcId": { "Ref": "Vpc" },
        "Tags": [
          {"Key": "Name", "Value": "{}-nodes-{}".format(options.dns_name, az)}
        ]
      }
    }

  # ---- Internet Gateway ------------------------------------------------------
  # Nothing special here, adds a route to the public internet from each subnet

  data["Resources"]["InternetGateway"] = {
    "Type": "AWS::EC2::InternetGateway",
    "Properties": {
      "Tags": [
        {"Key": "Name", "Value": "{}-internet-gateway".format(options.dns_name)}
      ]
    }
  }

  data["Resources"]["VpcInternetGatewayAttachment"] = {
    "Type": "AWS::EC2::VPCGatewayAttachment",
    "Properties": {
      "VpcId": {"Ref": "Vpc"},
      "InternetGatewayId": {"Ref": "InternetGateway"}
    }
  }

  data["Resources"]["VpcRouteTable"] = {
    "Type": "AWS::EC2::Route",
    "Properties": {
      "DestinationCidrBlock": "0.0.0.0/0",
      "RouteTableId": {"Ref": "RouteTable"},
      "GatewayId": {"Ref": "InternetGateway"}
    },
    "DependsOn": "VpcInternetGatewayAttachment"
  }

  data["Resources"]["RouteTable"] = {
    "Type": "AWS::EC2::RouteTable",
    "Properties": {"VpcId": {"Ref": "Vpc"}}
  }

  for az in ZONES:
    data["Resources"]["SubnetRouteTableAssociation" + AWSSafeString(az)] = {
      "Type": "AWS::EC2::SubnetRouteTableAssociation",
      "Properties": {
        "SubnetId": {"Ref": "VpcSubnet" + AWSSafeString(az)},
        "RouteTableId": {"Ref": "RouteTable"}
      }
    }

  # ---- DHCP ------------------------------------------------------------------
  # Nothing special here, but required boilerplate

  data["Resources"]["DhcpOptions"] = {
    "Type": "AWS::EC2::DHCPOptions",
    "Properties": {
      "DomainNameServers": [ "AmazonProvidedDNS" ]
    }
  }

  data["Resources"]["VpcDhpcOptionsAssociation"] = {
    "Type": "AWS::EC2::VPCDHCPOptionsAssociation",
    "Properties": {
      "VpcId": { "Ref": "Vpc" },
      "DhcpOptionsId": { "Ref": "DhcpOptions" }
    }
  }

  # ---- Network ACL -----------------------------------------------------------
  # Network ACLs that allow all outbound and inbound traffic (security is done
  # with security groups).

  data["Resources"]["NetworkAcl"] = {
    "Type": "AWS::EC2::NetworkAcl",
    "Properties": {"VpcId": {"Ref": "Vpc"}}
  }

  data["Resources"]["NetworkAclAllowAllEgress"] = {
    "Type": "AWS::EC2::NetworkAclEntry",
    "Properties": {
      "CidrBlock": "0.0.0.0/0",
      "Egress": True,
      "Protocol": "-1",
      "RuleAction": "allow",
      "RuleNumber": "100",
      "NetworkAclId": {
        "Ref": "NetworkAcl"
      }
    }
  }

  data["Resources"]["NetworkAclAllowAllIngress"] = {
    "Type": "AWS::EC2::NetworkAclEntry",
    "Properties": {
      "CidrBlock": "0.0.0.0/0",
      "Protocol": "-1",
      "RuleAction": "allow",
      "RuleNumber": "100",
      "NetworkAclId": {
        "Ref": "NetworkAcl"
      }
    }
  }

  # Attach a network ACL to each subnet
  for az in ZONES:
    data["Resources"]["SubNetAcl" + AWSSafeString(az)] = {
      "Type": "AWS::EC2::SubnetNetworkAclAssociation",
      "Properties": {
        "NetworkAclId": {"Ref": "NetworkAcl"},
        "SubnetId": {"Ref": "VpcSubnet" + AWSSafeString(az)}
      }
    }
