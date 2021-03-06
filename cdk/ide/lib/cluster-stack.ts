// import * as cdk from '@aws-cdk/core';
// import * as eks from '@aws-cdk/aws-eks';
// import * as ec2 from '@aws-cdk/aws-ec2';
// import * as s3 from '@aws-cdk/aws-s3';
// import * as iam from '@aws-cdk/aws-iam';
// import * as cr from '@aws-cdk/custom-resources';
// import * as logs from '@aws-cdk/aws-logs';
// import * as lambda from '@aws-cdk/aws-lambda';
import * as path from "path";
import {
  Duration,
  Stack,
  StackProps,
  CfnParameter,
  CustomResource,
  CfnOutput,
} from "aws-cdk-lib";
import * as sns from "aws-cdk-lib/aws-sns";
import * as subs from "aws-cdk-lib/aws-sns-subscriptions";
import * as sqs from "aws-cdk-lib/aws-sqs";
import { aws_s3 as s3 } from "aws-cdk-lib";
import { aws_ec2 as ec2 } from "aws-cdk-lib";
import { custom_resources as cr } from "aws-cdk-lib";
import { aws_iam as iam } from "aws-cdk-lib";
import { aws_logs as logs } from "aws-cdk-lib";
import { aws_lambda as lambda } from "aws-cdk-lib";
import { aws_codebuild as codebuild } from "aws-cdk-lib";
import { aws_events as events } from "aws-cdk-lib";
import { aws_events_targets as targets } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as cloud9 from "@aws-cdk/aws-cloud9-alpha";

const KeyName = "workshop";

export interface ClusterStackProps extends StackProps {
  vpcId: string;
  cloud9EnvironmentId: string;
  codeBuildRoleArn: string;
}
export class ClusterStack extends Stack {
  constructor(scope: Construct, id: string, props: ClusterStackProps) {
    super(scope, id, props);

    // Tag the stack and its resources.
    this.tags.setTag("StackName", "ClusterStack");

    // The VPC ID is supplied by the caller from the VPC_ID environment variable.
    const vpc = ec2.Vpc.fromLookup(this, "VPC", {
      vpcId: props.vpcId,
    });

    // CodeBuild role is supplied by the caller from the BUILD_ROLE_ARN environment variable.
    const codeBuildRole = iam.Role.fromRoleArn(
      this,
      "CodeBuildRole",
      props.codeBuildRoleArn
    );

    // MOVED TO FoundationStack

    /*     // Create an EC2 instance role for the Cloud9 environment. This instance
    // role is powerful, allowing the participant to have unfettered access to
    // the provisioned account. This might be too broad. It's possible to
    // tighten this down, but there may be unintended consequences.
    const instanceRole = new iam.Role(this, "WorkspaceInstanceRole", {
      assumedBy: new iam.ServicePrincipal("ec2.amazonaws.com"),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName("AdministratorAccess"),
      ],
      description: "Workspace EC2 instance role",
    });
 */

    // MOVED to FoundationStack
    /*     // During internal testing we found that Isengard account baselining
    // was attaching IAM roles to instances in the background. This prevents
    // the stack from being cleanly destroyed, so we will record the instance
    // role name and use it later to delete any attached policies before
    // cleanup.
    new CfnOutput(this, "WorkspaceInstanceRoleName", {
      value: instanceRole.roleName,
    });
 
    const instanceProfile = new iam.CfnInstanceProfile(
      this,
      "WorkspaceInstanceProfile",
      {
        roles: [instanceRole.roleName],
      }
    );
*/
    // Obtain Cloud9 workspace instance ID and security group.
    const workspaceInstance = new cr.AwsCustomResource(
      this,
      "WorkspaceInstance",
      {
        policy: cr.AwsCustomResourcePolicy.fromSdkCalls({
          resources: cr.AwsCustomResourcePolicy.ANY_RESOURCE,
        }),
        onUpdate: {
          service: "EC2",
          action: "describeInstances",
          physicalResourceId: cr.PhysicalResourceId.of(
            props.cloud9EnvironmentId
          ),
          parameters: {
            Filters: [
              {
                Name: "tag:aws:cloud9:environment",
                Values: [props.cloud9EnvironmentId],
              },
            ],
          },
          outputPaths: [
            "Reservations.0.Instances.0.InstanceId",
            "Reservations.0.Instances.0.NetworkInterfaces.0.Groups.0.GroupId",
          ],
        },
      }
    );
    const instanceId = workspaceInstance.getResponseField(
      "Reservations.0.Instances.0.InstanceId"
    );

    const workspaceSecurityGroup = ec2.SecurityGroup.fromSecurityGroupId(
      this,
      "WorkspaceSecurityGroup",
      workspaceInstance.getResponseField(
        "Reservations.0.Instances.0.NetworkInterfaces.0.Groups.0.GroupId"
      )
    );

    // MOVED to FoundationStack
    // This function provides a Custom Resource that detaches any existing IAM
    // instance profile that might be attached to the Cloud9 Environment, and
    // replaces it with the profile+role we created ourselves.
    /*     const fileFunction = new lambda.Function(this, "fileFunction", {
      code: lambda.Code.fromAsset(
        path.join(__dirname, "update-instance-profile")
      ),
      //handler: "index.onEventHandler",
      //runtime: lambda.Runtime.NODEJS_14_X,
      handler: "handler.lambda_handler",
      runtime: lambda.Runtime.PYTHON_3_9,
    });
    fileFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          "ec2:DescribeIamInstanceProfileAssociations",
          "ec2:ReplaceIamInstanceProfileAssociation",
          "ec2:AssociateIamInstanceProfile",
          "ec2:DescribeInstances",
          "iam:PassRole",
          "ssm:DescribeInstanceInformation",
        ],
        resources: ["*"], // TODO: use specific instance ARN
      })
    );

    const file = new cr.Provider(this, "fileProvider", {
      onEventHandler: fileFunction,
    });

    new CustomResource(this, "file", {
      serviceToken: file.serviceToken,
      properties: {
        InstanceId: instanceId,
        InstanceProfileArn: instanceProfile.attrArn,
      },
    });
 */

    // TODO: Remove this NOT NEEDED
    // Create an SSH key pair for logging into the K8S nodes.
    /*     const sshKeyPair = new cr.AwsCustomResource(this, "SSHKeyPair", {
      policy: cr.AwsCustomResourcePolicy.fromSdkCalls({
        resources: cr.AwsCustomResourcePolicy.ANY_RESOURCE,
      }),
      onCreate: {
        service: "EC2",
        action: "createKeyPair",
        physicalResourceId: cr.PhysicalResourceId.of(KeyName),
        parameters: {
          KeyName,
          KeyType: "rsa",
        },
        outputPaths: ["KeyName", "KeyMaterial"],
      },
      onDelete: {
        service: "EC2",
        action: "deleteKeyPair",
        parameters: {
          KeyName,
        },
      },
    });

    const keyMaterial = sshKeyPair.getResponseField("KeyMaterial");
    const keyName = sshKeyPair.getResponseField("KeyName");

 */

    /*     
    // Create our EKS cluster.
    const cluster = new eks.Cluster(this, "Cluster", {
      vpc,
      version: eks.KubernetesVersion.V1_21,
      clusterName: "security-workshop",
      defaultCapacity: 0,
      mastersRole: instanceRole,
    });

    // Enable cluster logging. See https://github.com/aws/aws-cdk/issues/4159
    new cr.AwsCustomResource(this, "ClusterLogsEnabler", {
      policy: cr.AwsCustomResourcePolicy.fromSdkCalls({
        resources: [`${cluster.clusterArn}/update-config`],
      }),
      onCreate: {
        physicalResourceId: { id: `${cluster.clusterArn}/LogsEnabler` },
        service: "EKS",
        action: "updateClusterConfig",
        region: this.region,
        parameters: {
          name: cluster.clusterName,
          logging: {
            clusterLogging: [
              {
                enabled: true,
                types: [
                  "api",
                  "audit",
                  "authenticator",
                  "controllerManager",
                  "scheduler",
                ],
              },
            ],
          },
        },
      },
    });

    // Allow CodeBuild environment to make changes to the cluster.
    cluster.awsAuth.addRoleMapping(codeBuildRole, {
      groups: ["system:masters"],
    });

    cluster.connections.allowFrom(workspaceSecurityGroup, ec2.Port.tcp(443));
    cluster.connections.allowFrom(workspaceSecurityGroup, ec2.Port.tcp(22));

    // Create a launch template for our EKS managed nodegroup that configures
    // kubelet with a staticPodPath.
    const userData = new ec2.MultipartUserData();
    userData.addUserDataPart(ec2.UserData.forLinux());
    userData.addCommands(
      "set -x",
      "echo Adding staticPodPath configuration to kubelet config file",
      "mkdir -p /etc/kubelet.d",
      "yum -y install jq",
      "jq '.staticPodPath=\"/etc/kubelet.d\"' < /etc/kubernetes/kubelet/kubelet-config.json > /tmp/kubelet-config.json",
      "mv /tmp/kubelet-config.json /etc/kubernetes/kubelet/kubelet-config.json",
      "systemctl restart kubelet"
    );

    const launchTemplate = new ec2.LaunchTemplate(this, "NodeLaunchTemplate", {
      userData,
      keyName,
    });

    // Create Managed Nodegroup.
    const nodegroup = new eks.Nodegroup(this, "ng-1", {
      cluster,
      desiredSize: 3,
      instanceTypes: [
        ec2.InstanceType.of(ec2.InstanceClass.M5A, ec2.InstanceSize.LARGE),
      ],
      subnets: vpc.selectSubnets({
        subnetType: ec2.SubnetType.PRIVATE_WITH_NAT,
      }),
      launchTemplateSpec: {
        // See https://github.com/aws/aws-cdk/issues/6734
        id: (launchTemplate.node.defaultChild as ec2.CfnLaunchTemplate).ref,
        version: launchTemplate.latestVersionNumber,
      },
    });

    // During internal testing we found that Isengard account baselining
    // was attaching IAM roles to instances in the background. This prevents
    // the stack from being cleanly destroyed, so we will record the instance
    // role name and use it later to delete any attached policies before
    // cleanup.
    new cdk.CfnOutput(this, "NodegroupRoleName", {
      value: nodegroup.role.roleName,
    });

    // Create an S3 bucket for forensics collection.
    const forensicsBucket = new s3.Bucket(this, "ForensicsBucket", {
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
      versioned: true,
      blockPublicAccess: {
        blockPublicAcls: true,
        blockPublicPolicy: true,
        ignorePublicAcls: true,
        restrictPublicBuckets: true,
      },
    }); */

    // Since Cloud9 has the SSM agent on it, we'll take advantage of its
    // presence to prepare the instance. This includes installing kubectl,
    // setting up the kubeconfig file, and installing the SSH private key
    // into the default user's home directory. We can add more steps later
    // if we like.

    // First, allow SSM to write Run Command logs to CloudWatch Logs. This
    // will allow us to diagnose problems later.
    const runCommandRole = new iam.Role(this, "RunCommandRole", {
      assumedBy: new iam.ServicePrincipal("ssm.amazonaws.com"),
    });
    const runCommandLogGroup = new logs.LogGroup(this, "RunCommandLogs");
    runCommandLogGroup.grantWrite(runCommandRole);

    // Now, invoke RunCommand.
    /*     new cr.AwsCustomResource(this, "InstancePrep", {
      installLatestAwsSdk: true,
      policy: cr.AwsCustomResourcePolicy.fromStatements([
        new iam.PolicyStatement({
          actions: ["iam:PassRole"],
          resources: [runCommandRole.roleArn],
        }),
        new iam.PolicyStatement({
          actions: ["ssm:SendCommand"],
          resources: ["*"],
        }),
      ]),
      onUpdate: {
        service: "SSM",
        action: "sendCommand",
        physicalResourceId: cr.PhysicalResourceId.of(props.cloud9EnvironmentId),
        parameters: {
          DocumentName: "AWS-RunShellScript",
          DocumentVersion: "$LATEST",
          InstanceIds: [instanceId],
          TimeoutSeconds: 30,
          ServiceRoleArn: runCommandRole.roleArn,
          CloudWatchOutputConfig: {
            CloudWatchLogGroupName: runCommandLogGroup.logGroupName,
            CloudWatchOutputEnabled: true,
          },
          Parameters: {
            commands: [
              // Add commands here to taste.
              // Set environment variables
              "sudo yum -y install jq bash-completion",
              'echo "export AWS_DEFAULT_REGION=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region`" >>  ~/.bash_profile',
              'echo "export AWS_ACCOUNT_ID=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .accountId`" >>  ~/.bash_profile',
              ".  ~/.bash_profile",

              // Clone the workshop repo
              "cd ~/environment;git clone https://github.com/aws-samples/policy-as-code.git",
              // Resize the instance volume
              "bash ~/environment/policy-as-code/cdk/cicd/resize.sh 100",
              // Install Rust and Cargo
              "curl https://sh.rustup.rs -sSf | sh -s -- -y ",
              "source $HOME/.cargo/env",
              // Install cfn-guard
              "cargo install cfn-guard",
              //"$ curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/aws-cloudformation/cloudformation-guard/main/install-guard.sh | sh",
              // Install Checkov
              "pip3 install checkov",
              // Install Open Policy Agent CLI
              "cd ~ && curl -L -o opa https://openpolicyagent.org/downloads/v0.34.2/opa_linux_amd64_static && chmod 755 ./opa",
              // Install Regula
              "wget https://github.com/fugue/regula/releases/download/v1.6.0/regula_1.6.0_Linux_x86_64.tar.gz",
              "mkdir ~/bin && tar xvzf regula_1.6.0_Linux_x86_64.tar.gz -C ~/bin regula",
              // Install cfn-lint
              "pip install cfn-lint",

              // "mv /tmp/kubectl /usr/local/bin/kubectl",
              // `su -l -c 'aws eks update-kubeconfig --name ${cluster.clusterName} --region ${this.region} --role-arn ${instanceRole.roleArn}' ec2-user`,
              // `su -l -c 'echo "export FORENSICS_S3_BUCKET=${forensicsBucket.bucketName}" >> ~/.bash_profile' ec2-user`,
              // `su -l -c 'mkdir -p ~/.ssh && chmod 700 ~/.ssh' ec2-user`,
              // // The key material isn't properly escaped, so we'll just base64-encode it first
              // `su -l -c 'echo "${cdk.Fn.base64(
              //   keyMaterial
              // )}" | base64 -d > ~/.ssh/id_rsa' ec2-user`,
              // `su -l -c 'chmod 600 ~/.ssh/id_rsa' ec2-user`,
              // 'curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp',
              // "chmod +x /tmp/eksctl",
              // "mv /tmp/eksctl /usr/local/bin",
              // "yum -y install jq gettext bash-completion moreutils",
              // "/usr/local/bin/kubectl completion bash > /etc/bash_completion.d/kubectl",
              // "/usr/local/bin/eksctl completion bash > /etc/bash_completion.d/eksctl",
              // `su -l -c 'echo "alias k=kubectl" >> ~/.bash_profile' ec2-user`,
              // `su -l -c 'echo "complete -F __start_kubectl k" >> ~/.bash_profile' ec2-user`,
            ],
          },
        },
        outputPaths: ["CommandId"],
      },
    });
 */
    // TODO: Install anything else we need
  }
}
