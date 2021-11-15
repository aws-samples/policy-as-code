---
title: "Introduction"
weight: 2
---
Developer, operation, and security teams can become familiar with implementing policy as code by understanding the tools designed for defining rules/policies. Projects like [cfn-guard](https://github.com/aws-cloudformation/cloudformation-guard) and [Open Policy Agent/Rego](https://www.openpolicyagent.org/docs/latest/#rego) offer high-level languages that can ease the development of rules. Other projects like [checkov](https://github.com/bridgecrewio/checkov), [cfn_nag](https://github.com/stelligent/cfn_nag), and [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) offer pre-defined rules. Both types of projects are necessary to craft a complete set of rules that cover standard best practices as well as organization specific policies. In this workshop participants will setup their development environment, learn to formulate rules for policy validation, run their rules through a CI/CD workflow, and explore detective controls for their policies. This workshop will take approximately 2 hours to complete end to end. Participants can also focus on specific areas as well.

## Infrastructure as Code (IaC)
Below is a list of IaC Projects that this workshop supports or will support.
- [Cloud Development Kit (CDK)](/introduction/cdk)
- [AWS Cloudformation](/introduction/cloudformation)
- [Terraform](/introduction/terraform)