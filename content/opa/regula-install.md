---
title: "Installing Regula"
weight: 41
---
## Overview
[Regula](https://regula.dev/) is a command line tool that uses rules written in [Rego](https://www.openpolicyagent.org/docs/latest/policy-language/) and was developed by [Fugue](https://www.fugue.co/). It is licensed under the [Apache License 2.0](https://github.com/fugue/regula/blob/master/LICENSE) This tool is used with the examples in this workshop but you can also use the [Open Policy Agent(OPA)](https://www.openpolicyagent.org/docs/latest/#running-opa)

## Installation
1. Download the regula binary from the releases page:
    ```bash
    cd ~/environment
    wget https://github.com/fugue/regula/releases/download/v1.6.0/regula_1.6.0_Linux_x86_64.tar.gz
    mkdir ~/bin && tar xvzf regula_1.6.0_Linux_x86_64.tar.gz -C ~/bin regula
    ```
1. Issue the command **regula** to validate that the installation worked:
    ```
    Regula

    Usage:
      regula [command]

    Available Commands:
      help              Help about any command
      init              Create a new Regula configuration file in the current working directory.
      repl              Start an interactive session for testing rules with Regula
      run               Evaluate rules against infrastructure as code with Regula.
      scan              Run regula and upload results to Fugue SaaS
      show              Show debug information.
      test              Run OPA test with Regula.
      version           Print version information.
      write-test-inputs Persist dynamically-generated test inputs for use with other Rego interpreters

    Flags:
      -h, --help      help for regula
      -v, --verbose   verbose output

    Use "regula [command] --help" for more information about a command.
    ```

::alert[The current version of Regula used in this workshop is v1.6.0. Later version may work just fine but users should always test and validate that.]