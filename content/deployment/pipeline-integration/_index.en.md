+++
title = "Integration with a pipeline"
weight = 61
+++

In this chapter we will demonstrate how to integrate CFGuard/OPA with a pipeline. Rule validation of the CF template will be executed as part of the deployment, failing to deploy should there be a violation.

Points to consider:
- How and Where do we store polices? -- see [Managing Polices](/advance-topics/managing-policies.html)
- Should we consolidate the validation process as one "stage" or segregate them to multiple. i.e running OPA and CFGuard as two separate stages, or a combination of rules(strict rule) as a stage, and additional optional rules as another stage.
- What is the expected action when a rule/stage fails?
- At what part of the pipeline would it make sense to integrate the validation?
- Providing local validation for developers for fast response, rather than deploying the source code as a pipeline


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
