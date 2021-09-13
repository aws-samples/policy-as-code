---
title: "Scanning Templates"
weight: 32
---
### Checkov Scanning
* Checkov has a large built in library for a variety of AWS Resouces for multiple Languages. 

* Create a new file called `cfn.yaml` and add this content to new file
* This Role has a very dangerous admin policy which a developer should not adding to any IAM Role, Checkov will find multiple issues with the policy 
```yaml
Resources:
  TestSecurityGroup:
    Type: "AWS::EC2::SecurityGroup"
    Properties:
      GroupDescription: Lint
      SecurityGroupIngress:
        - CidrIp: 0.0.0.0/0
          Description: Allow anyone to connect to port 80
          FromPort: 80
          IpProtocol: tcp
          ToPort: 80
      VpcId:
        Ref: Vpc8378EB38
    Metadata:
      aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  RootRole:
    Type: 'AWS::IAM::Role'
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - ec2.amazonaws.com
            Action:
              - 'sts:AssumeRole'
      Path: /
      Policies:
        - PolicyName: root
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action: '*'
                Resource: '*'
```
* Run Checkov on the directory `checkov -s --directory .`
* This example will fail `CKV_AWS_110` "Ensure IAM policies does not allow privilege escalation"


### Checkov Supression
* With Checkov, you can add inline comments into your code to supress a specific rule with a comment. 
* Add this line below `RootRole`
`#checkov:skip=CKV_AWS_110`
* Run Checkov again `checkov -s --directory .` and you will see `        SKIPPED for resource: AWS::IAM::Role.RootRole`
* You can also skip checks at the command line: `checkov -s --directory . --skip-check CKV_AWS_110`