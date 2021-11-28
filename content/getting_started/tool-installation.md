---
title: "Installing the Tools"
weight: 40
---

This section will cover the installation of the tools needed to run through this workshop as well as the deployment of the AWS CodePipeline.

1. Install the command line tools by running these commands:
    ```bash
    cd ~/environment/policy-as-code
    source ./cdk/ide/scripts/bootstrap.sh
    ```

Next explore one of these sections:
- [Preventative Controls](/pac-action/preventative)
    - [AWS CDK/CF and CloudFormation Guard](/pac-action/preventative/cfn-validation)
    - [Terraform HCL and Regula/OPA](/pac-action/preventative/hcl-validation)
- [CloudFormation Guard Basics](/pac-tools/cfn-guard/the-basics)
