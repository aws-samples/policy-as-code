---
title: "Installing CFN Lint"
weight: 13
---

The following steps describe how to install CFN Lint

We strongly suggest you checkout:

- This Page has the most up to date instructions
- [CFN Lint](https://github.com/aws-cloudformation/cfn-lint)

::alert[ **NOTE**: If you are attending an AWS Hosted Event to do this workshop OR you ran the bootstrap.sh script earlier, this step is not necessary! Only do this step if you elected not to run the bootstrap.sh script.]

## Install CFN Lint CLI

###Python

```bash
pip install cfn-lint
```

### Verify CFN Lint Installation

Check to see that you can run the cli for cfn-lint on your terminal.

```
$ cfn-lint

usage:
Basic: cfn-lint test.yaml
Ignore a rule: cfn-lint -i E3012 -- test.yaml
Configure a rule: cfn-lint -x E3012:strict=false -t test.yaml
Lint all yaml files in a folder: cfn-lint dir/**/*.yaml

CloudFormation Linter

optional arguments:
  -h, --help            show this help message and exit

Standard:
  TEMPLATE              The CloudFormation template to be linted
  -t TEMPLATE [TEMPLATE ...], --template TEMPLATE [TEMPLATE ...]
                        The CloudFormation template to be linted
  -b, --ignore-bad-template
                        Ignore failures with Bad template
  --ignore-templates IGNORE_TEMPLATES [IGNORE_TEMPLATES ...]
                        Ignore templates
  -f {quiet,parseable,json,junit,pretty}, --format {quiet,parseable,json,junit,pretty}
                        Output Format
  -l, --list-rules      list all the rules
  -r REGIONS [REGIONS ...], --regions REGIONS [REGIONS ...]
                        list the regions to validate against.
  -i IGNORE_CHECKS [IGNORE_CHECKS ...], --ignore-checks IGNORE_CHECKS [IGNORE_CHECKS ...]
                        only check rules whose id do not match these values
  -c INCLUDE_CHECKS [INCLUDE_CHECKS ...], --include-checks INCLUDE_CHECKS [INCLUDE_CHECKS ...]
                        include rules whose id match these values
  -m MANDATORY_CHECKS [MANDATORY_CHECKS ...], --mandatory-checks MANDATORY_CHECKS [MANDATORY_CHECKS ...]
                        always check rules whose id match these values, regardless of template exclusions
  -e, --include-experimental
                        Include experimental rules
  -x CONFIGURE_RULES [CONFIGURE_RULES ...], --configure-rule CONFIGURE_RULES [CONFIGURE_RULES ...]
                        Provide configuration for a rule. Format RuleId:key=value. Example: E3012:strict=false
  --config-file CONFIG_FILE
                        Specify the cfnlintrc file to use
  -z CUSTOM_RULES, --custom-rules CUSTOM_RULES
                        Allows specification of a custom rule file.
  -v, --version         Version of cfn-lint
  --output-file OUTPUT_FILE
                        Writes the output to the specified file, ideal for producing reports
  --merge-configs       Merges lists between configuration layers

Advanced / Debugging:
  -D, --debug           Enable debug logging
  -I, --info            Enable information logging
  -a APPEND_RULES [APPEND_RULES ...], --append-rules APPEND_RULES [APPEND_RULES ...]
                        specify one or more rules directories using one or more --append-rules arguments.
  -o OVERRIDE_SPEC, --override-spec OVERRIDE_SPEC
                        A CloudFormation Spec override file that allows customization
  -g, --build-graph     Creates a file in the same directory as the template that models the template's resources in DOT format
  -s REGISTRY_SCHEMAS [REGISTRY_SCHEMAS ...], --registry-schemas REGISTRY_SCHEMAS [REGISTRY_SCHEMAS ...]
                        one or more directories of CloudFormation Registry Schemas
  -u, --update-specs    Update the CloudFormation Specs

```
