---
title: "Open Policy Agent"
weight: 20
---

### What is Open Policy Agent?
The Open Policy Agent (OPA) is an open source, general-purpose policy engine that unifies policy enforcement across the stack. OPA provides a high-level declarative language that lets you specify policy as code.

OPA uses a policy language (inspired by [Datalog](https://en.wikipedia.org/wiki/Datalog)) called Rego. Rego queries are assertions on data stored in OPA. These queries can be used to define policies that enumerate instances of data that violate the expected state of the system.
Rego focuses on providing powerful support for referencing nested documents and ensuring that queries are correct and unambiguous.
Rego is declarative so policy authors can focus on what queries should return rather than how queries should be executed. These queries are simpler and more concise than the equivalent in an imperative language.
<br><br>
You can use OPA to enforce policies in microservices, Kubernetes, CI/CD pipelines, API gateways, and more.

### How Do I use OPA?
OPA is a binary that works as command line interface (CLI). This can be installed and run on your local machine, pipeline, container or as a service. Here are more [details](https://www.openpolicyagent.org/docs/latest/#running-opa).

### Why use Regula?
OPA has been used within the Kubernetes community and is probably the most well known cli tool for validating Rego rules. Regula is another option and comes with a set of rules targeted for AWS Cloudformation, Terraform, as well as Kubernetes YAML manifests. Regula is designed to work with Cloudformation and Terraform and so developers working with these artifacts may find the reporting and usage simpler and more intutive. However, either tool should work with the examples in this workshop.

### Reference
* [Open Policy Agent](https://www.openpolicyagent.org/docs/latest/)
* [Rego](https://www.openpolicyagent.org/docs/latest/policy-language/)
* [Regula](https://regula.dev/) 