---
title: "DevSecOps Workflow"
weight: 10
---

## Overview
This section will explore using policy as code as a set of guardrails for IaC deployments. Policy as Code can serve as a gatekeeper for resource deployments that do not comply
with the policies an organization has established. This workshop will use [AWS CodePipeline](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html) however this pattern can be implemented using [Github Actions](https://docs.github.com/en/actions), [Gitlab CI/CD](https://docs.gitlab.com/ee/ci/), [Bitbucket Pipelines](https://bitbucket.org/product/features/pipelines) etc.

The AWS CodePipeline will be used to deploy a compliant S3 bucket. Here is a typical policy that needs to be enforced:

>***AWS S3 buckets need to be deployed in a secure manner. We require encryption using strong and industry standard cryptography methods for data at rest and transit. - [NIST-800-53-SC-13](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#!/control?version=5.1&number=SC-13)
>There should be no public access and access should be restricted to the account that writes the data. Least privileged access should be enforced. - [NIST 800-53-8(2)](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#!/control?version=5.1&number=SA-8)***

An IaC developer will need to develop a set of rules to enforce the policy stated above. Here is a list of rules that will be used to enforce the policy above:
* ***Use S3 Block Public Access***
* ***Configure server-side encryption of S3 buckets***
* ***Use AWS managed keys for encryption of data in S3 bucket***
* ***Use a bucket policy to enforce HTTPS(TLS) connections only when reading or writing data***
* ***Use a bucket policy to enforce server-side encryption during object puts/writes to bucket***
* ***AWS KMS key used with the S3 bucket needs to have automatic rotation***
* ***AWS KMS key policy should not allow cross-account key access***

Fortunately the rules have already been written. The objective of this section of the workshop is to write the IaC code to pass the rules above. The outcome will be the successfully deployment of a compliant S3 bucket.

::alert[The AWS CodePipeline in this workshop is for educational and demo purposes only.]
