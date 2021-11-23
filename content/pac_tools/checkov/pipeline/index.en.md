---
title: "Deploying with a Pipeline"
weight: 33
---
### Pipeline Scanning

* Using Checkov for CloudFormation means that the code must be scanned before calling the `cloudformation:create_stack` or `cloudformation:update_stack` API.
* You will need to control exit codes from the Checkov command to move to the next stage. 

* Checkov can also be configured to read from a config file
    * Forcing Checkov to use a config file means that a centralized team can control Checkov settings at a variety of different levels such as business unit, application, groups of repositories, etc.
    * Developers should not be able to edit Checkov settings
    * There is an order of precedence from where the config file is read
        * `--directory` flag
        * Current working directory
        * Users Home Directory
    * A developer will most likely be able to include their own config file and copy it to a location that Checkov reads before running, your organization will have to decide how to mitigate this risk
    * The config files for Checkov must be managed in a central repository and Pipeline CI Jobs consume this file from a trusted source

### Creating a config file
* In the same directory that you created the CloudFormation template, create a file called `config.yml`
* We are going to try and silence AWS_CKV_21 for S3 Bucket versioning
* Run the command `checkov --directory . --config-file config.yaml`
* The results should include an error for S3 Bucket Versioning not being enabled
* Add the following lines to `config.yml`
```yaml
skip-check:
  - CKV_AWS_21 # Bucket Versioning
soft-fail-on:
  - CKV_AWS_18 # Access Logging
```
* Run the command again `checkov --directory . --config-file config.yaml`
* This will permanently skip the check about S3 Bucket Versioning not be enabled and will have Checkov run with a handful of specific flags that we need to review:
* Our organization has also decided that we will never stop S3 Access Logging not bneing configured from letting a Pipeline deploy, but we still want our users see the error, this is the use case for `soft-fail`
    * `soft-fail:false` This will have the command return 0 regardless of the findings, this should ALWAYS be set to false, otherwise you are scanning to see the results, but they will have no impact on the pipeline status. This flag basically disables Checkov.
    * `skip-checks:` This is a list of Checks that we are going to skip, this will completely hide the results for this check
    * `soft-fail-on` Instead of skipping checks, these checks will still run, but even if they fail, Checkov exits 0
      * This is useful for seeing the results of rules such as S3 Versioning or Access Logging without failing the Pipeline
