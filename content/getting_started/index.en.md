---
title: "Getting Started"
weight: 20
---

This section covers setting up your environment to work through the examples in this workshop. Deploying an [AWS Cloud9 environment](https://docs.aws.amazon.com/cloud9/latest/user-guide/welcome.html) will make setting this up a lot easier.

## Using your own AWS account
The environment needs to have the following tools installed.
1. [An AWS account](https://aws.amazon.com/getting-started/)
1. Setup AWS Cloud9 - [Create an environment](https://docs.aws.amazon.com/cloud9/latest/user-guide/tutorial-create-environment.html)
   * **Environment type** - Create a new no-ingress EC2 instance for environment (access via Systems Manager)
   * **Instance type** - Amazon Linux 2
1. Create a IAM role named **PolicyAsCodeRole** for configuring Cloud0 instance and deploying AWS CodePipeline [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_job-functions_create-policies.html) and select EC2 as the trusted entity. Choose the following AWS Managed Policies
   * AdministratorAccess
   * AWSCodeCommitPowerUser
   * AWSCodePipeline_ReadOnlyAccess
   * AWSCloud9SSMInstanceProfile
1. Attach the IAM role to the EC2 instance that has the prefix aws-cloud9-<**Name of the environment you've given it**>
1. Open your environment to Cloud9 specified [here](https://docs.aws.amazon.com/cloud9/latest/user-guide/open-environment.html)
1. Disable AWS managed temporary credentials in Cloud9 [settings](https://docs.aws.amazon.com/cloud9/latest/user-guide/security-iam.html#auth-and-access-control-temporary-managed-credentials).
1. Run the aws cli subcommand configure and leave everything blank but your region:
    ```
    aws configure
    AWS Access Key ID [None]: 
    AWS Secret Access Key [None]: 
    Default region name [None]: us-east-2 or whatever your actual region is.
    Default output format [None]:
    ```
1. Increase the volume size of your Cloud9 instance specified [here](https://docs.aws.amazon.com/cloud9/latest/user-guide/move-environment.html#move-environment-resize).
1. checkov - [Installing Checkov](/checkov/install-checkov)
    :::code{showCopyAction=true showLineNumbers=false}
    pip3 install checkov
    :::
1. Install [Rust](https://www.rust-lang.org/tools/install)
    :::code{showCopyAction=true showLineNumbers=false}
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh;source ~/.bash_profile
    :::
    Choose "1) Proceed with installation (default)" or hit enter.
1. cfn-guard - [Installing cfn-guard](https://github.com/aws-cloudformation/cloudformation-guard#installation)
    ```
    git clone https://github.com/dchakrav-github/cloudformation-guard
    cd cloudformation-guard
    git switch parameterized-rules
    cargo build --release
    mkdir -p ~/bin;cp ./target/release/cfn-guard ~/bin
    cfn-guard --version
    ```
1. Clone the policy-as-code repository from github in the environment directory:
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment;git clone https://github.com/aws-samples/policy-as-code.git
    :::
1. Install the AWS CodePipeline as follows:
    ```
    cd ~/environment/policy-as-code/cdk/cicd
    pip install -r requirements.txt
    cdk bootstrap
    cdk deploy --all
    ```
1. Answer 'y' to all prompts.
1. Remove AdministratorAccess from the IAM role **PolicyAsCodeRole**.

### AWS Hosted Event
* Obtain the **Event Hash** for [AWS Event Engine](https://dashboard.eventengine.run/login)
* An AWS CodePipeline should be provisioned for you skip to the next section [AWS CodePipeline Run](/deployment/pipeline-integration#aws-codepipeline-run)
