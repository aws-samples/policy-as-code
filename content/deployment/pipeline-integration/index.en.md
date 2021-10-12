---
title: "Policy as Code Pipeline"
weight: 61
---

## Overview
This section will explore using policy as code tools to provide guardrails for IaC deployments. Policy as Code tools serve as gatekeepers to resource deployments that do not comply
with the policies an organization has established. There are many CI/CD tools that can be used to implement this workflow but for this workshop AWS CodePipeline will be used. The
concepts used here would be applicable to any CI/CD tool.

This pipeline will be used to deploy a compliant S3 bucket. Here is a typical policy that needs to be enforced:

>***AWS S3 buckets need to be deployed in a secure manner. We require encryption using strong and industry standard cryptography methods for data at rest and transit.
>There should be no public access and access should be restricted to the account that writes the data.***

An IaC developer will need to develop a set of rules to enforce the policy stated above. Here is a list of rules that will be used to enforce the policy above:
* ***Use S3 Block Public Access***
* ***Configure server-side encryption of S3 buckets***
* ***Use AWS managed keys for encryption of data in S3 bucket***
* ***Use a bucket policy to enforce HTTPS(TLS) connections only when reading or writing data***
* ***Use a bucket policy to enforce server-side encryption during object puts/writes to bucket***

::alert[The AWS CodePipeline in this workshop is for educational and demo purposes only. Production pipelines should have least privileged access by IaC developers with the objective to limit blast radius. ]

## Getting Started
There are two options for running this part of the workshop:
* Running this workshop in your own AWS - [Using your own AWS account](/deployment/pipeline-integration#using-your-own-aws-account)
* Running a AWS Hosted Event - [AWS Hosted Event](/deployment/pipeline-integration#aws-hosted-event)

### Using your own AWS account
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
1. cfn-guard - [Installing cfn-guard](https://github.com/aws-cloudformation/cloudformation-guard#installation)
1. Clone the policy-as-code repository from github in the environment directory:
    :::code{showCopyAction=true showLineNumbers=false}
    cd environment;git clone https://github.com/aws-samples/policy-as-code.git
    :::
1. Install the AWS CodePipeline as follows:
:::code{showCopyAction=true showLineNumbers=false}
cd ~/environment/policy-as-code/cdk/cicd
pip install -r requirements.txt
cdk bootstrap
cdk deploy --all
:::
13. Answer 'y' to all prompts.
1. Remove AdministratorAccess from the IAM role **PolicyAsCodeRole**.

### AWS Hosted Event
* Obtain the **Event Hash** for [AWS Event Engine](https://dashboard.eventengine.run/login)
* An AWS CodePipeline should be provisioned for you skip to the next section [AWS CodePipeline Run](/deployment/pipeline-integration#aws-codepipeline-run)

## AWS CodePipeline Run
The S3 application is ready to be deployed. In order for it to be deployed successfully it must comply with the rules created as specified above.
To kickoff the deployment use git push to AWS CodeCommit which is the source for the pipeline. During this workshop the cdk/cfn template will be
changed to comply with the rules specified in the AWS CodePipeline. To start do the following:

1. Remove the reference to the upstream code repo by issues the command specified below:
:::code{showCopyAction=true showLineNumbers=false}
git remote remove origin
:::
2. Get the repository clone URL by running the the following commands:
:::code{showCopyAction=true showLineNumbers=false}
export repo=$(aws codecommit list-repositories --output text | awk '{print $3}' | grep policy-as-code)
aws codecommit get-repository --repository-name ${repo} --query 'repositoryMetadata.cloneUrlHttp' --output text
:::
3. Add the copied URL and make it a remote repo. The below is what it should look like. Note '<stack_id>' is the actual stack_id in the command issued above:
```
git remote add origin https://git-codecommit.us-east-2.amazonaws.com/v1/repos/policy-as-code-<stack_id>
```
4. Make sure that you have the git-remote-codecommit python package installed. This help with authenticating with CodeCommit.
:::code{showCopyAction=true}
pip install git-remote-codecommit
:::
5. Push the repo
:::code{showCopyAction=true showLineNumbers=false}
git push --set-upstream origin main
:::
6. View your CodePipeline in your account. Instructions to do that is [here](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-view-console.html#pipelines-list-console.)

:::code{showCopyAction=true showLineNumbers=false}
        kms_key = aws_kms.Key(self, 'KmsKey',
            enable_key_rotation=True
        )
        
        kms_key.add_to_resource_policy(
            aws_iam.PolicyStatement(
                actions=[
                    '*',
                    'kms:*'
                ],
                effect=aws_iam.Effect.DENY,
                principals=[
                        aws_iam.AnyPrincipal()
                ],
                resources=[
                        "*"
                ],
                conditions={'StringNotEquals': {'kms:CallerAccount': self.account}}
            )
        )
:::

:::code{showCopyAction=true showLineNumbers=false}
        unencrypted_put_conditions = [
            {'StringNotEquals': { 's3:x-amz-server-side-encryption': 'AES256'}},
            {'StringNotEquals': { 's3:x-amz-server-side-encryption': 'aws:kms'}},
            {'Null': {'s3:x-amz-server-side-encryption': True}}
        ]
        
        for condition in unencrypted_put_conditions:
            bucket.add_to_resource_policy(
                aws_iam.PolicyStatement(
                    actions=[
                        "s3:PutObject"
                    ],
                    effect=aws_iam.Effect.DENY,
                    principals=[
                        aws_iam.AnyPrincipal()
                    ],
                    resources=[
                        bucket.bucket_arn + "/*"
                    ],
                    conditions=condition
                )
            )
:::



## Useful Markdown - Ignore
[Managing Polices](/advance-topics/managing-policies.html)
- Should we consolidate the validation process as one "stage" or segregate them to multiple. i.e running OPA and CFGuard as two separate stages, or a combination of rules(strict rule) as a stage, and additional optional rules as another stage.
- Using any of these tools within your own environment will probably require building a Docker Image for your CI/CD tools to use as a build image - how will you maintain and publish this docker image?
## Architecture Diagram
{{< img "pipeline.png" "pipeline Architecture" >}}


## Building a custom pipeline stage
We will use CDK to create a custom pipeline stage and integrate it to a pipeline cdk construct. this can be added as a stage to an existing pipeline as well.
<br/>
We will create one stage for OPA and stage for CF Guard. lastly we will add the two custom stage in to a pipeline.
#### OPA Stage
```typescript
import {CdkPipeline, ShellScriptAction} from "@aws-cdk/pipelines";
import {Artifact} from "@aws-cdk/aws-codepipeline";

export const addOPAStage = (pipeline:CdkPipeline, sourceArtifact:Artifact) => {
  const OPAStage = pipeline.addStage('OPAStage');
  const shellScriptAction = new ShellScriptAction({
    actionName: "OPAalidation",
    commands: [
      'curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64',
      'chmod 755 ./opa',
      './opa version',
      'cd pipeline/opa',
      '../../opa test . -v'
    ],
    additionalArtifacts: [sourceArtifact],
    runOrder: OPAStage.nextSequentialRunOrder()
  });

  OPAStage.addActions(shellScriptAction);
}
```

#### CF Guard Stage
```typescript
import {CdkPipeline, ShellScriptAction} from "@aws-cdk/pipelines";
import {Artifact} from "@aws-cdk/aws-codepipeline";

export const addCFGuardStage = (pipeline:CdkPipeline, sourceArtifact:Artifact) => {

  const CFGuardStage = pipeline.addStage('CFGuardStage');
  const shellScriptAction = new ShellScriptAction({
    actionName: "CFGuardValidation",
    commands: [
      "cd pipeline",
      'ls -l',
      "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > installrust.sh",
      'chmod 775 installrust.sh',
      './installrust.sh -y',
      '. $HOME/.cargo/env',
      'wget https://github.com/aws-cloudformation/cloudformation-guard/releases/download/1.0.0/cfn-guard-linux-1.0.0.tar.gz',
      'tar -xvf cfn-guard-linux-1.0.0.tar.gz',
      './cfn-guard-linux/cfn-guard --version',
      'cd cfnguard',
      'cargo test',
      'cd ..',
      './cfn-guard-linux/cfn-guard check -r rules/ecs_apploadbalancer.ruleset -t test/foo.template.json'
    ],
    additionalArtifacts: [sourceArtifact],
    runOrder: CFGuardStage.nextSequentialRunOrder()
  });

  CFGuardStage.addActions(shellScriptAction);
}
```

{{% notice note %}}
  The stage creation includes the installation of OPA/CFGuard and depended on libraries
{{% /notice %}}

#### Adding stage to a pipeline

```typescript
mport * as cdk from '@aws-cdk/core';
import * as codepipeline from '@aws-cdk/aws-codepipeline';
import * as codepipeline_actions from '@aws-cdk/aws-codepipeline-actions';
import { CdkPipeline, SimpleSynthAction } from "@aws-cdk/pipelines";
import {addCFGuardStage} from "./cdk-cfguard-stage";
import {addOPAStage} from "./cdk-opa-stage";

export class MyCustomPipelinesStack extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const sourceArtifact = new codepipeline.Artifact();
        const cloudAssemblyArtifact = new codepipeline.Artifact();

        const pipeline = new CdkPipeline(this, 'myPipeline', {
            pipelineName: 'myCustomStagePipeline',
            cloudAssemblyArtifact,
          
            // Set a source for pipeline, using configuration fetched from a secret to access github
            sourceAction: new codepipeline_actions.GitHubSourceAction({
                actionName: 'GitHub',
                output: sourceArtifact,
                // @ts-ignore
                oauthToken: cdk.SecretValue.secretsManager('pipelineSecret', {
                    jsonField: 'githubToken'
                }),
                owner: cdk.SecretValue.secretsManager('pipelineSecret', {
                    jsonField: 'githubOwner'
                }).toString(),
                repo: cdk.SecretValue.secretsManager('pipelineSecret', {
                    jsonField: 'githubRepo'
                }).toString(),
                branch: cdk.SecretValue.secretsManager('pipelineSecret', {
                    jsonField: 'branch'
                }).toString()
            }),

            // Build and synthesize app to generate CF template --- you may use existing one and skip this step
            synthAction: new SimpleSynthAction({
                sourceArtifact,
                cloudAssemblyArtifact,
                subdirectory: 'pipeline',
                installCommands: [
                    'npm install -g aws-cdk',
                    'cdk --version',
                    'npm install',
                ],
                buildCommands: ['npm run build'],
                synthCommand: 'npx cdk synth'
            })
        });

        //Here we add the custom strage to the pipeline
        addCFGuardStage(pipeline, sourceArtifact)
        addOPAStage(pipeline, sourceArtifact)
    }
}

```
{{% notice note %}}
The last two lines is where we add our custom OPA/CF Guard stage.
{{% /notice %}}


{{% notice tip %}}
You can use the stage above regardless to the pipeline example and simply use the [pipeline.addStage](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-codepipeline.Pipeline.html)
{{% /notice %}}

Let's execute the pipeline:
```
cdk synth
```
Now deploy
```
cdk deploy
```
The new pipeline will be created and ready to execute - you may see the new custom stage as part of the pipeline. if a rule will fail the pipeline will break.
