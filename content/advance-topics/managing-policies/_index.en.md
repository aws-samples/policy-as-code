+++
title = "Managing Polices"
weight = 51
+++

We looked in to a few examples of writing rules in Rego and CFGuard. the next topic we will cover is how to manage rules, or a collective of rules - Polices.


## Rules Segregation
In most cases, it would make sense to segregate rules to individual files, so that they can be assembled in different context to create a policy.
<br/>
One approach is to segregate the rules by the resource they are applicable for under their domain i.e: networking, rds, ecs, s3, etc..

```markdown
    rules
    ├── common
    │   ├── common-functions.rego  
    ├── networking
    │   ├── check-sg-public-ip.rego
    │   ├── check-sg-all-ingress.rego
    │   ├── check-shared-sg.rego
    ├── s3
    │   ├── deny-unencrypted-buckets.rego  
    ├── rds
    │   ├── check-required-secret-for-password.rego
    │   ├── limit-db-size.rego
    └── _index.md
```
{{% notice note %}}
Similar approach can be taken for ruleset files - if CF Guard is used.
{{% /notice %}}

An alternative approach is to consolidate rules based on solutions/products or business organization segmentation - such as: compliance rules, security rules, risk and controls.

{{% notice tip %}}
In Rego, use the **import** statement to add functions and rules from another file or common module.
{{% /notice %}}

## Logical Polices
There are several ways of which we can create a policy. one way is to simply create an expression of the rules that needs to be evaluated as a policy. or iterate on the rules in a specific directory so that they will be executed consecutively 

```shell
./opa eval -f pretty --fail-defined -i input_template.json -d ./rules_directory data
```
 Policies can also be assembled on the fly to create custom policies based on Organization unit, title, or project related.


## Managing Rules and Polices
The mechanisms of managing rules and polices can be as simple as a repository contain all the rules, a database, or an interactive service to vend appropriate rules and polices.   
### Repository
Easiest to maintain, repository can be own by security team, allowing only them to create/modify rules and policies. Developer can have read only access, or use a tool with a limited access to fetch the rules and polices and run them locally.
<br/><br/>
Version control help in maintaining the version and history of every rule change. Git tags can be used to tag rules/polices release.

### Policy As Service
Building a service for vending rules and polices is a great way to achieve agility. service can provide custom polices based on a given criteria. 
Also service can easily integrate as part of a pipeline or workflow and provide more features to resolve the desired rules.

For more information on bundles [Read Here](https://www.openpolicyagent.org/docs/v0.12.2/bundles/)
