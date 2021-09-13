---
title: "Scanning Templates"
weight: 41
---

CFN Lint works with JSON and YAML CloudFormation templates including checks for Valid Values, Resource Properties and Best Practices. CFN Lint also allows for user defined rules
* CFN Lint is mostly for Linting Template structure and does not have many higher level rules out of the box for security scanning.
* We are going to start by overpermissioning an IAM Role with an Inline policy.
* Create a file called cfn.yml and populate with the content below
* ```yaml
    Resources:
      TestSecurityGroup:
        Type: "AWS::EC2::SecurityGroup"
        Properties:
          GroupDescription: Lint
          SecurityGroupIngress:
            - CidrIp: 0.0.0.0/0
              Description: Allow anyone to connect to port 80
              FromPort: 443
              IpProtocol: tcp
              ToPort: 80
          VpcId:
            Ref: Vpc8378EB38
        Metadata:
          aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
    ```


* Create a file called custom_rules.txt in the same directory as `cfn.yml`
* `AWS::EC2::SecurityGroup GroupDescription != "Lint" WARN "Must call your Group a specific name"`
* This rule will validate that Security Group Description is called "Lint"
* This rule will file when the FromPort is 80
* There is no way to write a rule that says "NO Port 80 when CidrIP is 0.0.0.0/0" at least with the Custom Syntax
* The key takeaway from writing these rules is that you cannot add more complex queries compared to CFN-Guard and OPA
* The rule engine used in CFN Lint is less easily customisable compared to CFN Guard
* If you are willing to write Python Code for the rules, you should be able to write more complex rules
* Writing Python Code is more difficult than managing CFN Guards DSL
* There may be a way to enable this functionality using [Python](https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/getting_started/rules.md)
* There is still use for CFN Lint in your automated Deployments, it can be combined with any of the other tools scanning tools here. 
* It usually makes sense to run CFN Lint before running another tool to scan your code. 
* Be careful of Exit Codes when using CFN Lint - there are a variety of categories that define your finding and some codes may unintentionally block your pipeline or deployment from proceeding. 