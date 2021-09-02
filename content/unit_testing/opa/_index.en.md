+++
title = "Open Policy Agent"
weight = 21
+++

The Open Policy Agent (opa) command line comes with a test subcommand for testing Rego policies. The following steps describe how to install **opa**. </br>

We strongly suggest you checkout: 
* [Running OPA](https://www.openpolicyagent.org/docs/latest/#running-opa)


### Install OPA CLI

The full instructions can be reviewed [here](https://www.openpolicyagent.org/docs/latest/#running-opa)

### Mac
```bash
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_darwin_amd64
```

### Linux
```bash
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
```

### Windows
```bash
https://openpolicyagent.org/downloads/latest/opa_windows_amd64.exe
```

### Verify OPA cli installation
Check to see that you can run the cli for opa on your terminal.

```
$ opa
An open source project to policy-enable your service.

Usage:
  opa [command]

Available Commands:
  bench       Benchmark a Rego query
  build       Build an OPA bundle
  check       Check Rego source files
  deps        Analyze Rego query dependencies
  eval        Evaluate a Rego query
  fmt         Format Rego source files
  help        Help about any command
  parse       Parse Rego source file
  run         Start OPA in interactive or server mode
  sign        Generate an OPA bundle signature
  test        Execute Rego test cases
  version     Print the version of OPA

Flags:
  -h, --help   help for opa

Use "opa [command] --help" for more information about a command.
```


### Creating Rego Policy Unit Tests

Once opa is installed create a project directory called **securitygroup** as described below.

```markdown
mkdir securitygroup
cd securitygroup
```

You'll be creating two files. One will be the Rego policy for validating your CF template. The other is the unit test for your Rego Policy. Let's start with the unit test file (in keeping with [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)) Create a file named **securitygroup_tests.rego** with contents show below

```
package securitygroup.allow_secured_ports_only

test_allow_secured_ports_only {
    not allow with input as {
    "Resources": {
        "CounterLBSecurityGroup63C1AB9D": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Automatically created Security Group for ELB fooCounterLBAEF24CE8",
                "SecurityGroupIngress": [{
                    "CidrIp": "0.0.0.0/0",
                    "Description": "Allow from anyone on port 80",
                    "FromPort": 80,
                    "IpProtocol": "tcp",
                    "ToPort": 80
                }],
                "VpcId": {
                    "Ref": "Vpc8378EB38"
                }
            },
            "Metadata": {
                "aws:cdk:path": "foo/Counter/LB/SecurityGroup/Resource"
            }
        }
    }
}}
```

Let's also create the rules file. The unit test is set to fail if the rules allow the snippet of cloudformation to pass with no issues. Our initial rules file always allow the cloudformation to pass. Let's create that file and discuss this a bit more.

```
package securitygroup.allow_secured_ports_only

resource_type = "AWS::EC2::SecurityGroup"

default allow = true

```

Next lets run our first test.

```
opa test . -v
FAILURES
--------------------------------------------------------------------------------
data.securitygroup.allow_secured_ports_only.test_allow_secured_ports_only: FAIL (264.006µs)

  query:1                        Enter data.securitygroup.allow_secured_ports_only.test_allow_secured_ports_only = _
  securitygroup_tests.rego:3     | Enter data.securitygroup.allow_secured_ports_only.test_allow_secured_ports_only
  securitygroup_tests.rego:4     | | Fail not data.securitygroup.allow_secured_ports_only.allow with input as {"Resources": {"CounterLBSecurityGroup63C1AB9D": {"Metadata": {"aws:cdk:path": "foo/Counter/LB/SecurityGroup/Resource"}, "Properties": {"GroupDescription": "Automatically created Security Group for ELB fooCounterLBAEF24CE8", "SecurityGroupIngress": [{"CidrIp": "0.0.0.0/0", "Description": "Allow from anyone on port 80", "FromPort": 80, "IpProtocol": "tcp", "ToPort": 80}], "VpcId": {"Ref": "Vpc8378EB38"}}, "Type": "AWS::EC2::SecurityGroup"}}}
  query:1                        | Fail data.securitygroup.allow_secured_ports_only.test_allow_secured_ports_only = _

SUMMARY
--------------------------------------------------------------------------------
data.securitygroup.allow_secured_ports_only.test_allow_secured_ports_only: FAIL (264.006µs)
--------------------------------------------------------------------------------
FAIL: 1/1
```

As expected our test fails because we are allowing the unit test snippet of cloudformation to pass. Because we use the **not allow with input as...** in our unit test we expect the cloudformation to be in violation of the policy we've written. We now need to craft a set of rules that successfully flags a violation of our policy. Let's do that by adding a set of rules. Let's modify the contents of our rules file, **securitygroup.rego** with the following:

```
package securitygroup.allow_secured_ports_only

resource_type = "AWS::EC2::SecurityGroup"

default allow = true


allow = false {
    count(deny_non_secure_ports) > 0
}

deny_non_secure_ports[resource] {
    some resource, j
    input.Resources[resource].Type == resource_type
    input.Resources[resource].Properties.SecurityGroupIngress[j].FromPort != 443
}{
    some resource, j
    input.Resources[resource].Type == resource_type
    input.Resources[resource].Properties.SecurityGroupIngress[j].ToPort != 443
}
```

Once you have updated your **securitygroup_tests.rego** let's re-run our test.

```
opa test . -v
data.securitygroup.allow_secured_ports_only.test_allow_secured_ports_only: PASS (445.252µs)
--------------------------------------------------------------------------------
PASS: 1/1
```

We have written our first unit test, watched it fail. We then wrote a set of rules to pass our test. At this point we should look at making this more robust. 
