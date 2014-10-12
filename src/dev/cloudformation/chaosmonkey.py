
def BuildChaosMonkey(options, data):

  # This builds a security policy that allows chaosmonkey to do its thing and
  # associates it with an IAM role. The IAM role is in turn associated with
  # each EC2 instance when it launches. This avoids the need for long-lived AWS
  # secret keys to be assigned to instances.
  chaosmonkey_policy = {
    "PolicyName": "ChaosMonkey",
    "PolicyDocument": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "Stmt1357739573947",
          "Action": [
            "ec2:CreateTags",
            "ec2:DeleteSnapshot",
            "ec2:DescribeImages",
            "ec2:DescribeInstances",
            "ec2:DescribeSnapshots",
            "ec2:DescribeVolumes",
            "ec2:TerminateInstances",
            "ses:SendEmail",
            "elasticloadbalancing:*"
          ],
          "Effect": "Allow",
          "Resource": "*"
        },
        {
          "Sid": "Stmt1357739649609",
          "Action": [
            "autoscaling:DeleteAutoScalingGroup",
            "autoscaling:DescribeAutoScalingGroups",
            "autoscaling:DescribeAutoScalingInstances",
            "autoscaling:DescribeLaunchConfigurations"
          ],
          "Effect": "Allow",
          "Resource": "*"
        },
        {
          "Sid": "Stmt1357739730279",
          "Action": [
            "sdb:BatchDeleteAttributes",
            "sdb:BatchPutAttributes",
            "sdb:DomainMetadata",
            "sdb:GetAttributes",
            "sdb:PutAttributes",
            "sdb:ListDomains",
            "sdb:CreateDomain",
            "sdb:Select"
          ],
          "Effect": "Allow",
          "Resource": "*"
        }
      ]
    }
  }

  data["Resources"]["ChaosMonkeyRole"] = {
    "Type": "AWS::IAM::Role",
    "Properties": {
      "AssumeRolePolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [{
          "Effect": "Allow",
          "Principal": {
            "Service": ["ec2.amazonaws.com"]
          },
          "Action": ["sts:AssumeRole"]
        }]
      },
      "Path": "/",
      "Policies": [chaosmonkey_policy],
    }
  }
