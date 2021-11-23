---
title: "Preventative Controls"
weight: 10
---

This section will use [AWS CodePipeline](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html) to validate an IaC deployment. It will reject IaC code that does not comply with a policy. This pattern can also be implemented using [Github Actions](https://docs.github.com/en/actions), [Gitlab CI/CD](https://docs.gitlab.com/ee/ci/), [Bitbucket Pipelines](https://bitbucket.org/product/features/pipelines) etc.

::alert[The AWS CodePipeline in this workshop is for educational and demo purposes only.]
