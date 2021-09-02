+++
title = "Installing Cloudformation Guard"
weight = 12
+++
The following steps describe how to install the cfn-guard cli. </br>

We strongly suggest you checkout: 
* [CloudFormation Guard](https://github.com/aws-cloudformation/cloudformation-guard)

## Install CloudFormation Guard CLI

The full instructions can be reviewed [here](https://github.com/aws-cloudformation/cloudformation-guard#installation)

### Ubuntu/Mac
Installation via pre-built binaries:
```
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/aws-cloudformation/cloudformation-guard/main/install-guard.sh | sh

```

For more options on [installation click here](https://github.com/aws-cloudformation/cloudformation-guard#installation)

### Windows
Refer to the [full instructions](https://github.com/aws-cloudformation/cloudformation-guard#installation)

### Verify the installation
Check to see that you can run the cli for cfn-guard and opa from your terminal and the version:

```
cfn-guard --version
```
You should see:

```
cfn-guard 2.0
```

For additional help:
```
cfn-guard -h
```
## Clone the workshop repo examples

```bash
git clone TBD
```

Once cloned, navigate to thr workshop resources directory which all command will be based this root path.
```bash
cd /policy-as-code-workshop/resources
```