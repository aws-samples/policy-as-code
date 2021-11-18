// CloudFormation constructs
import {
  Duration,
  Stack,
  StackProps,
  CfnParameter,
  CustomResource,
  CfnOutput,
} from "aws-cdk-lib";

// Services used by this stack
import {
  aws_s3 as s3,
  aws_ec2 as ec2,
  aws_iam as iam,
  aws_lambda as lambda,
  aws_codebuild as codebuild,
  aws_events as events,
  aws_events_targets as targets,
  custom_resources as cr,
} from "aws-cdk-lib";

// Higher order constructs
import * as cloud9 from "@aws-cdk/aws-cloud9-alpha";

// CDK stuff
import { Construct } from "constructs";
import { Handler } from "aws-cdk-lib/lib/aws-lambda";

// Other typescript modules
import * as path from "path";

// This function is based on the cfnresponse JS module that is published
// by CloudFormation. It's an async function that makes coding much easier.

// TODO: Remove this - replaced with new lambda code based on crhelper Python framework
const respondFunction = `
const respond = async function(event, context, responseStatus, responseData, physicalResourceId, noEcho) {
  return new Promise((resolve, reject) => {
    var responseBody = JSON.stringify({
        Status: responseStatus,
        Reason: "See the details in CloudWatch Log Stream: " + context.logGroupName + " " + context.logStreamName,
        PhysicalResourceId: physicalResourceId || context.logStreamName,
        StackId: event.StackId,
        RequestId: event.RequestId,
        LogicalResourceId: event.LogicalResourceId,
        NoEcho: noEcho || false,
        Data: responseData
    });

    console.log("Response body:\\n", responseBody);

    var https = require("https");
    var url = require("url");

    var parsedUrl = url.parse(event.ResponseURL);
    var options = {
        hostname: parsedUrl.hostname,
        port: 443,
        path: parsedUrl.path,
        method: "PUT",
        headers: {
            "content-type": "",
            "content-length": responseBody.length
        }
    };

    var request = https.request(options, function(response) {
        console.log("Status code: " + response.statusCode);
        console.log("Status message: " + response.statusMessage);
        resolve();
    });

    request.on("error", function(error) {
        console.log("respond(..) failed executing https.request(..): " + error);
        resolve();
    });

    request.write(responseBody);
    request.end();
  });
};
`;

// Properties needed for the stack
export interface FoundationStackProps extends StackProps {
  sourceZipFile: string;
  sourceZipFileChecksum: string;
}

export class FoundationStack extends Stack {
  constructor(scope: Construct, id: string, props: FoundationStackProps) {
    super(scope, id, props);

    // These parameters appear to be supplied by Event Engine. We'll
    // take advantage of them to locate the Zip file containing this
    // source code.
    const assetBucketName = new CfnParameter(this, "EEAssetsBucket", {
      default: "BucketNameNotSet",
      type: "String",
    });

    const assetPrefix = new CfnParameter(this, "EEAssetsKeyPrefix", {
      default: "KeyPrefixNotSet",
      //default: "modules/local_testing/v1/",
      type: "String",
    });

    const teamRoleArn = new CfnParameter(this, "EETeamRoleArn", {
      default: "RoleNotSet", // set this for testing in non-EE environment
      type: "String",
    });

    // We supply the value of this parameter ourselves via the ZIPFILE
    // environment variable. It will be automatically rendered into the
    // generated YAML template.
    const sourceZipFile = new CfnParameter(this, "SourceZipFile", {
      default: props.sourceZipFile,
      type: "String",
    });

    const sourceZipFileChecksum = new CfnParameter(
      this,
      "SourceZipFileChecksum",
      {
        default: props.sourceZipFileChecksum,
        type: "String",
      }
    );

    const assetBucket = s3.Bucket.fromBucketName(
      this,
      "SourceBucket",
      assetBucketName.valueAsString
    );

    // We need to create the Cloud9 environment here, instead of in the cluster stack
    // created in CodeBuild, so that the stack creator can access the environment.
    // (CodeBuild builds perform in a different role context, which makes the
    // environment inaccessible.)
    //

    // ------VPC------
    const vpc = new ec2.Vpc(this, "VPC", {
      maxAzs: 2,
      cidr: "10.0.0.0/16",
      natGateways: 1,
      subnetConfiguration: [
        {
          subnetType: ec2.SubnetType.PUBLIC,
          name: "Public",
          cidrMask: 18,
        },
        {
          subnetType: ec2.SubnetType.PRIVATE_WITH_NAT,
          name: "Private",
          cidrMask: 18,
        },
      ],
    });

    // ------CodeBuild------
    // Most of the resources will be provisioned via CDK. To accomplish this,
    // we will leverage CodeBuild as the execution engine for a Custom Resource.
    /*     const buildProjectRole = new iam.Role(this, "BuildProjectRole", {
      assumedBy: new iam.ServicePrincipal("codebuild.amazonaws.com"),
    });
    const buildProjectPolicy = new iam.Policy(this, "BuildProjectPolicy", {
      statements: [
        new iam.PolicyStatement({
          // TODO: Scope this down
          actions: ["*"],
          resources: ["*"],
        }),
      ],
    });
    buildProjectRole.attachInlinePolicy(buildProjectPolicy);

    const buildProject = new codebuild.Project(this, "BuildProject", {
      role: buildProjectRole,
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
        computeType: codebuild.ComputeType.SMALL,
      },
      source: codebuild.Source.s3({
        bucket: assetBucket,
        path: `${assetPrefix.valueAsString}${sourceZipFile.valueAsString}`,
      }),
      timeout: Duration.minutes(15),
    });
 */
    // Custom resource function to start a build. The "application" being built
    // deploys our CDK app containing additional resources for attendees
    /*     const startBuildFunction = new lambda.Function(this, "StartBuildFunction", {
      code: lambda.Code.fromInline(
        respondFunction +
          `
const AWS = require('aws-sdk');

exports.handler = async function (event, context) {
  console.log(JSON.stringify(event, null, 4));
  try {
    const projectName = event.ResourceProperties.ProjectName;
    const codebuild = new AWS.CodeBuild();

    console.log(\`Starting new build of project \${projectName}\`);

    const { build } = await codebuild.startBuild({
      projectName,
      // Pass CFN related parameters through the build for extraction by the
      // completion handler.
      buildspecOverride: event.RequestType === 'Delete' ? 'cdk/ide/buildspec-destroy.yml' : 'cdk/ide/buildspec.yml',
      environmentVariablesOverride: [
        {
          name: 'CFN_RESPONSE_URL',
          value: event.ResponseURL
        },
        {
          name: 'CFN_STACK_ID',
          value: event.StackId
        },
        {
          name: 'CFN_REQUEST_ID',
          value: event.RequestId
        },
        {
          name: 'CFN_LOGICAL_RESOURCE_ID',
          value: event.LogicalResourceId
        },
        {
          name: 'VPC_ID',
          value: event.ResourceProperties.VpcId
        },
        {
          name: 'CLOUD9_ENVIRONMENT_ID',
          value: event.ResourceProperties.Cloud9EnvironmentId
        },
        {
          name: 'BUILD_ROLE_ARN',
          value: event.ResourceProperties.BuildRoleArn
        }
      ]
    }).promise();
    console.log(\`Build id \${build.id} started - resource completion handled by EventBridge\`);
  } catch(error) {
    console.error(error);
    await respond(event, context, 'FAILED', { Error: error });
  }
};
      `
      ),
      handler: "index.handler",
      runtime: lambda.Runtime.NODEJS_14_X,
      timeout: Duration.minutes(1),
    });
    startBuildFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["codebuild:StartBuild"],
        resources: [buildProject.projectArn],
      })
    );

    // Lambda function to execute once CodeBuild has finished producing a build.
    // This will signal CloudFormation that the build (i.e., deploying the actual
    // infra stack for the workshop) has completed.
    const reportBuildFunction = new lambda.Function(
      this,
      "ReportBuildFunction",
      {
        code: lambda.Code.fromInline(
          respondFunction +
            `
const AWS = require('aws-sdk');

exports.handler = async function (event, context) {
  console.log(JSON.stringify(event, null, 4));

  const projectName = event['detail']['project-name'];

  const codebuild = new AWS.CodeBuild();

  const buildId = event['detail']['build-id'];
  const { builds } = await codebuild.batchGetBuilds({
    ids: [ buildId ]
  }).promise();

  console.log(JSON.stringify(builds, null, 4));

  const build = builds[0];
  // Fetch the CFN resource and response parameters from the build environment.
  const environment = {};
  build.environment.environmentVariables.forEach(e => environment[e.name] = e.value);

  const response = {
    ResponseURL: environment.CFN_RESPONSE_URL,
    StackId: environment.CFN_STACK_ID,
    LogicalResourceId: environment.CFN_LOGICAL_RESOURCE_ID,
    RequestId: environment.CFN_REQUEST_ID,
    // Must be constant, otherwise CloudFormation will attempt to delete the
    // resource after completing an update
    PhysicalResourceId: 'build'
  };

  if (event['detail']['build-status'] === 'SUCCEEDED') {
    await respond(response, context, 'SUCCESS', {});
  } else {
    await respond(response, context, 'FAILED', { Error: 'Build failed' });
  }
};
      `
        ),
        handler: "index.handler",
        runtime: lambda.Runtime.NODEJS_14_X,
        timeout: Duration.minutes(1),
      }
    );
    reportBuildFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["codebuild:BatchGetBuilds", "codebuild:ListBuildsForProject"],
        resources: [buildProject.projectArn],
      })
    );

    // Trigger the CloudFormation notification function upon build completion.
    const buildCompleteRule = new events.Rule(this, "BuildCompleteRule", {
      description: "Build complete",
      eventPattern: {
        source: ["aws.codebuild"],
        detailType: ["CodeBuild Build State Change"],
        detail: {
          "build-status": ["SUCCEEDED", "FAILED", "STOPPED"],
          "project-name": [buildProject.projectName],
        },
      },
      targets: [new targets.LambdaFunction(reportBuildFunction)],
    });

    // Kick off the build (CDK deployment).
    const clusterStack = new CustomResource(this, "ClusterStack", {
      serviceToken: startBuildFunction.functionArn,
      properties: {
        ProjectName: buildProject.projectName,
        VpcId: vpc.vpcId,
        // Cloud9EnvironmentId: workspace.environmentId,
        BuildRoleArn: buildProjectRole.roleArn,
        // This isn't actually used by the custom resource. We use a change in
        // the checksum as a way to signal to CloudFormation that the input has
        // changed and therefore the stack should be redeployed.
        ZipFileChecksum: sourceZipFileChecksum.valueAsString,
      },
    });
    clusterStack.node.addDependency(buildCompleteRule, buildProjectPolicy, vpc);

 */ // ------Cloud9------
    const workspace = new cloud9.Ec2Environment(this, "Workspace", {
      vpc: vpc,
      ec2EnvironmentName: "aws-workshop",
      description: "AWS Event Workshop",
      // Can't use t3a instances for Cloud9 due to silly server-side regex filter. Oh, well.
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.T3,
        ec2.InstanceSize.MEDIUM
      ),
      subnetSelection: { subnetType: ec2.SubnetType.PUBLIC },
    });

    // Output the Cloud9 IDE URL
    new CfnOutput(this, "URL", { value: workspace.ideUrl });

    // CLOUD9 - INSTANCE PROFILE
    // --------------------------------------------------------------------------------
    // Create an EC2 instance role for the Cloud9 environment. This instance
    // role is powerful, allowing the participant to have unfettered access to
    // the provisioned account. This might be too broad. It's possible to
    // tighten this down, but there may be unintended consequences.
    const instanceRole = new iam.Role(this, "WorkspaceInstanceRole", {
      assumedBy: new iam.ServicePrincipal("ec2.amazonaws.com"),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName("AdministratorAccess"),
      ],
      description: "Cloud9 Workspace EC2 instance role",
    });

    // During internal testing we found that Isengard account baselining
    // was attaching IAM roles to instances in the background. This prevents
    // the stack from being cleanly destroyed, so we will record the instance
    // role name and use it later to delete any attached policies before
    // cleanup.
    new CfnOutput(this, "WorkspaceInstanceRoleName", {
      value: instanceRole.roleName,
    });

    // Create an instance profile for the Cloud9 environment.
    const instanceProfile = new iam.CfnInstanceProfile(
      this,
      "WorkspaceInstanceProfile",
      {
        roles: [instanceRole.roleName],
      }
    );

    // ------------LAMBDA EXECUTION ROLE----------------
    // Build IAM role for custom resource lambda functions to initialize Cloud9
    const lambdaRole = new iam.Role(this, "Cloud9InitializtionLambdaRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
      description: "Execution role for Cloud9 bootstrapping functions",
    });

    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        actions: [
          "cloudformation:DescribeStackResources",
          "ec2:AssociateIamInstanceProfile",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus",
          "ec2:DescribeInstanceAttribute",
          "ec2:DescribeIamInstanceProfileAssociations",
          "ec2:DescribeVolumes",
          "ec2:DesctibeVolumeAttribute",
          "ec2:DescribeVolumesModifications",
          "ec2:DescribeVolumeStatus",
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ssm:DescribeInstanceInformation",
          "ec2:ModifyVolume",
          "ec2:ReplaceIamInstanceProfileAssociation",
          "ec2:ReportInstanceStatus",
          "ssm:SendCommand",
          "ssm:GetCommandInvocation",
          "s3:GetObject",
        ],
        resources: ["*"], //TODO: Refactor and scope this down
      })
    );

    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ["iam:PassRole"],
        resources: [instanceRole.roleArn],
      })
    );

    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ["lambda:AddPermission", "lambda:RemovePermission"],
        resources: ["*"],
      })
    );

    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        actions: [
          "events:PutRule",
          "events:DeleteRule",
          "events:PutTargets",
          "events:RemoveTargets",
        ],
        resources: ["*"],
      })
    );

    // Create a membership to grant access to the Cloud9 instance
    const createMembership = new cr.AwsCustomResource(
      this,
      "Cloud9CreateMembership",
      {
        policy: cr.AwsCustomResourcePolicy.fromSdkCalls({
          resources: cr.AwsCustomResourcePolicy.ANY_RESOURCE,
        }),
        onCreate: {
          service: "Cloud9",
          action: "createMembership",
          physicalResourceId: cr.PhysicalResourceId.of(workspace.environmentId),
          parameters: {
            environmentId: workspace.environmentId,
            permissions: "read-write",
            userArn: teamRoleArn.valueAsString,
          },
        },
      }
    );

    // Attach instance profile to the Cloud9 environment via Lambda backed custom resource
    // Thanks to maishsk@ for this code: https://gitlab.aws.dev/maishsk/cloud9-event-engine-cfn-template

    const updateInstanceProfileFunction = new lambda.Function(
      this,
      "UpdateInstanceProfileFunction",
      {
        code: lambda.Code.fromAsset(path.join(__dirname, "c9InstanceProfile")),
        handler: "lambda_function.handler",
        role: lambdaRole,
        runtime: lambda.Runtime.PYTHON_3_9,
        timeout: Duration.minutes(1),
      }
    );

    const updateInstanceProfileProvider = new cr.Provider(
      this,
      "UpdateInstanceProfileProvider",
      {
        onEventHandler: updateInstanceProfileFunction,
      }
    );
    new CustomResource(this, "UpdateInstanceProfile", {
      serviceToken: updateInstanceProfileProvider.serviceToken,
      properties: {
        InstanceProfile: instanceProfile.attrArn,
        Cloud9Environment: workspace.ec2EnvironmentArn,
      },
    });

    // CLOUD9 - DISK RESIZE
    // --------------------------------------------------------------------------------
    // Resize the EBS volume attached to the Cloud9 EC2 instance
    // Thanks to maishsk@ for this code: https://gitlab.aws.dev/maishsk/cloud9-event-engine-cfn-template

    const diskResizeFunction = new lambda.Function(
      this,
      "Cloud9DiskResizeFunction",
      {
        code: lambda.Code.fromAsset(path.join(__dirname, "c9DiskResize")),
        handler: "lambda_function.handler",
        role: lambdaRole,
        runtime: lambda.Runtime.PYTHON_3_9,
        timeout: Duration.minutes(1),
      }
    );

    const diskResizeProvider = new cr.Provider(
      this,
      "Cloud9DiskResizeProvider",
      {
        onEventHandler: diskResizeFunction,
      }
    );

    new CustomResource(this, "Cloud9ResizeDisk", {
      serviceToken: diskResizeProvider.serviceToken,
      properties: {
        EBSVolumeSize: 32, //TODO: Parameterize this?
      },
    });

    // CLOUD9 - BOOTSTRAP
    // --------------------------------------------------------------------------------
    // Finish configuring the Cloud9 environment, e.g. installing packages, running scripts
    // Thanks to maishsk@ for this code: https://gitlab.aws.dev/maishsk/cloud9-event-engine-cfn-template

    const bootstrapFunction = new lambda.Function(
      this,
      "Cloud9BootstrapFunction",
      {
        code: lambda.Code.fromAsset(path.join(__dirname, "c9bootstrap")),
        handler: "lambda_function.handler",
        role: lambdaRole,
        runtime: lambda.Runtime.PYTHON_3_9,
        timeout: Duration.minutes(1),
      }
    );

    const bootstrapProvider = new cr.Provider(this, "Cloud9BootstrapProvider", {
      onEventHandler: bootstrapFunction,
    });

    new CustomResource(this, "Cloud9Bootstrap", {
      serviceToken: bootstrapProvider.serviceToken,
      properties: {
        InstanceId: instanceProfile.attrArn,
        BootstrapPath:
          "s3://" + assetBucketName + "/" + assetPrefix + "/bootstrap.sh",
        BootstrapArguments: "",
      },
    });
  }
}
