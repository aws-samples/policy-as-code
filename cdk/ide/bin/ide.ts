#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { FoundationStack } from "../lib/ide-stack";
//import { ClusterStack } from "../lib/cluster-stack";
// import { BootstrapStack } from '../lib/bootstrap-stack';

// From CDK workshop stack
import "source-map-support/register";
// Upgraded to aws-cdk-lib above
//import * as cdk from '@aws-cdk/core';

const app = new cdk.App();
new FoundationStack(app, "FoundationStack", {
  sourceZipFile: process.env.ZIPFILE || "workshop-stack-app.zip",
  sourceZipFileChecksum: process.env.ZIPFILE_CHECKSUM || "",
  sourceZipURI: process.env.S3_URL || "",
});

// See below for example when FoundationStack needs environment
// new BootstrapStack(app, 'BootstrapStack', {
//     sourceZipFile: process.env.ZIPFILE || 'eks-workshop-stack-app.zip',
//     sourceZipFileChecksum: process.env.ZIPFILE_CHECKSUM || '',
//   });

// TODO: Determine if we really need a second stack
// Create a second stack for CICD, etc.
/* new ClusterStack(app, "ClusterStack", {
  env: {
    region: process.env.AWS_REGION || process.env.AWS_DEFAULT_REGION,
    account: process.env.AWS_ACCOUNT_ID,
  },
  vpcId: process.env.VPC_ID || "VPC_ID_NOT_SET",
  cloud9EnvironmentId:
    process.env.CLOUD9_ENVIRONMENT_ID || "CLOUD9_ENVIRONMENT_ID_NOT_SET",
  codeBuildRoleArn:
    process.env.BUILD_ROLE_ARN || "arn:aws:123456789012::iam:role/NOT_SET",
});
 */
