---
title: "Installing Regula"
weight: 10
---

## Overview

[Regula](https://regula.dev/) is a command line tool that uses [OPA](https://www.openpolicyagent.org/docs/latest/#running-opa) to evaluate rules written in [Rego](https://www.openpolicyagent.org/docs/latest/policy-language/) and was developed by [Fugue](https://www.fugue.co/). It evaluates AWS Cloudformation templates, Terraform HCL code, Terraform JSON plans, and Kubernetes YAML manifests and is licensed under the [Apache License 2.0.](https://github.com/fugue/regula/blob/master/LICENSE) This tool is used with the examples in this workshop but you can also use the [Open Policy Agent(OPA)](https://www.openpolicyagent.org/docs/latest/#running-opa)

::alert[ **NOTE**: If you are attending an AWS Hosted Event to do this workshop OR you ran the bootstrap.sh script earlier, this step is not necessary! Only do this step if you elected not to run the bootstrap.sh script.]

## Installation

1. Download the regula binary from the releases page:
   ```bash
   cd ~/environment
   wget https://github.com/fugue/regula/releases/download/v2.0.1/regula_2.0.1_Linux_x86_64.tar.gz
   mkdir ~/bin && tar xvzf regula_2.0.1_Linux_x86_64.tar.gz -C ~/bin regula
   ```
1. Issue the command **regula** to validate that the installation worked:

   ```
   Regula

   Usage:
     regula [command]

   Available Commands:
     completion        generate the autocompletion script for the specified shell
     help              Help about any command
     init              Create a new Regula configuration file in the current working directory.
     repl              Start an interactive session for testing rules with Regula
     run               Evaluate rules against infrastructure as code with Regula.
     show              Show debug information.
     test              Run OPA test with Regula.
     version           Print version information.
     write-test-inputs Persist dynamically-generated test inputs for use with other Rego interpreters

   Flags:
     -h, --help      help for regula
     -v, --verbose   verbose output

   Use "regula [command] --help" for more information about a command.
   ```

::alert[The current version of Regula used in this workshop is v2.0.1.]
