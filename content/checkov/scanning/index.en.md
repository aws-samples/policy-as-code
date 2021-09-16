---
title: "Scanning Templates"
weight: 32
---
### Checkov Scanning
* Checkov has a large built in library for a variety of AWS Resouces for multiple Languages. 
* The main reason for AWS Developers to use Checkov is support for CloudFormation and Terraform
* Create a new file called `cfn.yaml` and add this content to new file or download the file from the assets repo
* The template contains a role has a very dangerous admin policy which a developer should not be adding to any IAM Role, Checkov will find multiple issues with the policy. There is also a default S3 Bucket here which will trigger a handful of less critical findings that we will use an example.
* See code below
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
    #checkov:skip=CKV_AWS_110 Admin policy required
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
  S3Bucket:
    Type: 'AWS::S3::Bucket'
    DeletionPolicy: Retain
    Properties:
      BucketName: DOC-EXAMPLE-BUCKET
```
* Run Checkov on the directory `checkov -s --directory .`
* This example will fail `CKV_AWS_110` "Ensure IAM policies does not allow privilege escalation"

### Review Findings
* The S3 Bucket Resource will trigger a handful of results that need to be addressed
    * CKV_AWS_19
    * CKV_AWS_18
    * CKV_AWS_53
    * CKV_AWS_54
    * CKV_AWS_21
    * CKV_AWS_55
    * CKV_AWS_56
* Checkov results usually include a range of risk you are mitigating, but there is no way to filter by risk
    * For example: This S3 Bucket does not include Versioning or Access Logging - these are optional features that do not always need to be enabled
    * This S3 Bucket also does not include the block to Disable Public Access, which your organization may require
* Your organization will need to determine which failed checks to ignore and let the pipeline proceed and which checks that must be resolved


### Checkov Supression
* With Checkov, you can add inline comments into your code to supress a specific rule with a comment.
* Inline comments and Supressions sit with the templates that your Developers are creating
* Add this line below `RootRole`
`#checkov:skip=CKV_AWS_110 Admin Role required`
* Run Checkov again `checkov -s --directory .` and you will see `SKIPPED for resource: AWS::IAM::Role.RootRole`
* You can also skip checks at the command line: `checkov -s --directory . --skip-check CKV_AWS_110`
* Add this line below `S3Bucket`
`#checkov:skip=CKV_AWS_21 No S3 Versioning Required`
  

### Conclusion
* Determining which checks to fail your pipeline on is much easier than writing the rules that Checkov has already implemented from scratch.
* You can write your own custom Checkov rules - they are written in Python. Checkov regulary accepts Pull Requests on the public repo, but this is not required to integrate your custom checks. 
* Checkov might not be your preferred tool to write new checks for, but it has such a large existing rulespace and is well maintained that it makes sense to include it in most CloudFormation and Terraform Pipelines
* Here is a [simple example](https://github.com/bridgecrewio/checkov/pull/1546/commits/68adc6f9e5c45a7cf7981b626efdc5d0ac301eab) of a pull request that has been merged to check for Lambda environment variable encryption if a KMS Key is provided