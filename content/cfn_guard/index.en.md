---
title: "AWS Cloudformation Guard"
chapter: true
weight: 30
---

This section focuses on using AWS CloudFormation Guard to validate CloudFormation templates. Policy as code can be developed using [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development) (TDD). CloudFormation Guard makes this really easy because the command line utility (cfn-guard) supports unit tests. In this section we will focus on creating our policy as code in three steps:

**Specify the rules that will enforce our policy**
   
**Create a unit test that would test the rule we write**
   
**Write a rule that will pass the unit test**
