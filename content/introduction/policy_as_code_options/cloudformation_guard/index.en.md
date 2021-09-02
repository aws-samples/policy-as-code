---
title: "AWS CloudFormation Guard"
weight: 15
---

### What is AWS CloudFormation Guard?
AWS CloudFormation Guard(cfn-guard) provides compliance administrators with a simple, policy-as-code language to define rules that can check for both required and prohibited resource configurations.
It enables developers to validate their CloudFormation templates against those rules.

cfn-guard helps enterprises minimize risks related to overspending on operating costs, security vulnerabilities, legal issues, and more. For example, administrators can create rules to ensure that developers always create encrypted Amazon S3 buckets. cfn-guard has a lightweight, declarative syntax that allows administrators to define rules quickly without needing to learn a programming language.
<br><br>
Developers can use cfn-guard either locally while editing templates or automatically as part of a CI/CD pipeline to stop deployment of non-compliant resources. If resources in the template fail the rules, cfn-guard provides developers information to help identify non-compliant resources.

### Using AWS Cloudformation Guard
cfn-guard is an open-source command line interface (CLI) that checks CloudFormation templates for policy compliance using a simple, policy-as-code, declarative language.
Once Installed, you can run the command line with a given template input along with a ruleset, cfn-guard will evaluate the rules against the template and provide the results back.

### Rules Semantic
Cloudformation guard supports applying rules as a single/multi line logical expression which can be encapsulated on single/multiple ".ruleset" files
<br><br>
We should keep the methodology simple as in "single rule per one ruleset file"
<br>
The Language currently supports:
* Apply basic logical operators i.e: [==,<=,>=,<,>,|OR|,!=]
* General acceptance nouns i.e: [NONE,ANY,*]
* Collection check i.e [IN,NOT_IN]
* Regex expressions
* Conditional rules WHEN clause

### Reference
[CloudFormation Guard CLI](https://github.com/aws-cloudformation/cloudformation-guard#installation) <br>
[CloudFormation Guard](https://aws.amazon.com/about-aws/whats-new/2020/10/aws-cloudformation-guard-an-open-source-cli-for-infrastructure-compliance-is-now-generally-available/#:~:text=Customer%20Enablement-,AWS%20CloudFormation%20Guard%20%E2%80%93%20an%20open%2Dsource%20CLI%20for%20infrastructure,compliance%20%E2%80%93%20is%20now%20generally%20available&text=Cfn%2Dguard%20is%20an%20open,as%2Dcode%2C%20declarative%20language.)