# ---
# title: "Open Policy Agent - Optional"
# weight: 13
# ---
The following steps describe how to install the Open Policy Agent (opa) cli. </br>

We strongly suggest you checkout: 
* [Running OPA](https://www.openpolicyagent.org/docs/latest/#running-opa)


## Install OPA CLI

The full instructions can be reviewed [here](https://www.openpolicyagent.org/docs/latest/#running-opa)

###Mac
```bash
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_darwin_amd64
```

###Linux
```bash
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
```

###Windows
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

## Clone the workshop repo examples

```bash
git clone TBD
```

Once cloned, navigate to thr workshop resources directory which all command will be based this root path.
```bash
cd /policy-as-code-workshop/resources
```