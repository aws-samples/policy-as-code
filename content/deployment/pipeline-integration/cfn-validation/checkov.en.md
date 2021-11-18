---
title: "Fix checkov findings"
weight: 30
---

## Remediate checkov rule violations
1. The two issues flagged by [checkov](https://github.com/bridgecrewio/checkov) are as follows:
    * CKV_AWS_53: "Ensure S3 bucket has block public ACLS enabled"
    * CKV_AWS_19: "Ensure the S3 bucket has server-side-encryption enabled"
1. To validate the same issue locally. Run the following commands:
   :::code{showCopyAction=true showLineNumbers=false}
   # Commands to setup CDK app locally, generate cfn template, and validate with checkov
   cd ~/environment/policy-as-code/cdk/app/
   pip install -r requirements.txt
   cdk synth
   checkov --directory cdk.out --config-file ./rules/checkov/checkov-config.yml
   :::
1. Verify that the same issues that checkov flagged in codebuild exists in the local environment.
1. CDK generated the CFN template that is in violation. Examine the CFN template by opening the file **cdk.out/policy-as-code.template.json** in the Cloud9 IDE:
    ![PolicyAsCodeTmpl](/static/PolicyAsCodeTmpl.png)
    Note the PublicAccessBlockConfiguration that checkov flagged:
    ```
    ...
    "PublicAccessBlockConfiguration": {
      "BlockPublicAcls": false,
      "BlockPublicPolicy": true,
      "IgnorePublicAcls": true,
      "RestrictPublicBuckets": true
    },
    ...
    ```
    The **BlockPublicAcls** has been set to **false** this needs to be **true**. To fix this go to the CDK source file that generated this template.
1. Open the file **s3_deployment.py** in the Cloud9's editor/IDE.
    ![S3DeploymentTree](/static/S3DeploymentTree.png)
    Find the section in the file that looks like this:
    ```
    ...
    block_public_access=aws_cdk.aws_s3.BlockPublicAccess(
        # Uncomment block_public_acls=True and remove block_public_acls=False
        # block_public_acls=True,
        block_public_acls=False,
        restrict_public_buckets=True,
        block_public_policy=True,
        ignore_public_acls=True
    )
    ...
    ```
    Here block_public_acls=False has been explicitly set. Remove that line and Uncomment the line of
    code above it. It will look like this:
    ```
    ...
    block_public_access=aws_cdk.aws_s3.BlockPublicAccess(
        # Uncomment block_public_acls=True and remove block_public_acls=False
        block_public_acls=True,
        restrict_public_buckets=True,
        block_public_policy=True,
        ignore_public_acls=True
    )
    ...
    ```
    Save the file in Cloud9 editor by clicking on **File**
    ![S3DeploymentFileSave.png](/static/S3DeploymentFileSave.png)
1. Run the following commands to see if the code change will fix this:
   :::code{showCopyAction=true showLineNumbers=false}
   cdk synth; checkov --directory cdk.out --config-file ./rules/checkov/checkov-config.yml
   :::
1. At this point there should only be one issue with checkov:
   ```
   ...
   Check: CKV_AWS_19: "Ensure the S3 bucket has server-side-encryption enabled"
        FAILED for resource: AWS::S3::Bucket.Bucket83908E77
        File: /policy-as-code.template.json:3-50
        Guide: https://docs.bridgecrew.io/docs/s3_14-data-encrypted-at-rest

                3  |     "Bucket83908E77": {
                4  |       "Type": "AWS::S3::Bucket",
                5  |       "Properties": {
   ...
   ```
1. To enable server-side-encryption encryption of the S3 bucket, open the file **cdk.out/policy-as-code.template.json** in Cloud9. Remember that since we are using a CDK app to create this CloudFormation template, you should edit the CDK App instead of the Rendered CloudFormaœtion. 
    ```
    ...
    "Bucket83908E77": {
      "Type": "AWS::S3::Bucket",
      "Properties": {
        "LifecycleConfiguration": {...},
        "PublicAccessBlockConfiguration": {...},
        "Tags": [...],
        "VersioningConfiguration": {...}
      },
      "UpdateReplacePolicy": "Delete",
      "DeletionPolicy": "Delete",
      "Metadata": {
        "aws:cdk:path": "policy-as-code/Bucket/Resource"
      }
    }
    ...
    ```
    The property **BucketEncryption** is not set. Modify the CDK code to generate the CFN template that will set this property. Open the file **s3_deployment.py** and find the code that matches:
    ```
        ...
        # Uncommment to make checkov pass
        # encryption=aws_s3.BucketEncryption.S3_MANAGED,
        ...
    ```
    Uncomment **encryption=aws_s3.BucketEncryption.S3_MANAGED,** it should look like this:
    ```
        ...
        # Uncommment to make checkov pass
        encryption=aws_s3.BucketEncryption.S3_MANAGED,
        ...
    ```
    Save the file in Cloud9 and run:
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code/cdk/app/; cdk synth
    :::
    Open the file **cdk.out/policy-as-code.template.json** and inspect the CFN template:
    ```
    ...
    "Bucket83908E77": {
      "Type": "AWS::S3::Bucket",
      "Properties": {
        "BucketEncryption": {
          "ServerSideEncryptionConfiguration": [
            {
              "ServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
              }
            }
          ]
        },
        "LifecycleConfiguration": {...},
        "PublicAccessBlockConfiguration": {...},
        "Tags": [...],
        "VersioningConfiguration": {...}
      },
      "UpdateReplacePolicy": "Delete",
      "DeletionPolicy": "Delete",
      "Metadata": {
        "aws:cdk:path": "policy-as-code/Bucket/Resource"
      }
    }
    ...
    ```
    The CFN Template has the **BucketEncryption** property set.
1. Run checkov to validate the template:
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code/cdk/app/;checkov --directory cdk.out --config-file ./rules/checkov/checkov-config.yml
    :::
    The output should look like this, with all 8 tests passing:
    ```
    cloudformation scan results:

    Passed checks: 8, Failed checks: 0, Skipped checks: 0

    Check: CKV_AWS_53: "Ensure S3 bucket has block public ACLS enabled"
            PASSED for resource: AWS::S3::Bucket.Bucket83908E77
            File: /policy-as-code.template.json:3-59
            Guide: https://docs.bridgecrew.io/docs/bc_aws_s3_19

    Check: CKV_AWS_54: "Ensure S3 bucket has block public policy enabled"
            PASSED for resource: AWS::S3::Bucket.Bucket83908E77
            File: /policy-as-code.template.json:3-59
            Guide: https://docs.bridgecrew.io/docs/bc_aws_s3_20

    Check: CKV_AWS_19: "Ensure the S3 bucket has server-side-encryption enabled"
            PASSED for resource: AWS::S3::Bucket.Bucket83908E77
            File: /policy-as-code.template.json:3-59
            Guide: https://docs.bridgecrew.io/docs/s3_14-data-encrypted-at-rest

    Check: CKV_AWS_55: "Ensure S3 bucket has ignore public ACLs enabled"
            PASSED for resource: AWS::S3::Bucket.Bucket83908E77
            File: /policy-as-code.template.json:3-59
            Guide: https://docs.bridgecrew.io/docs/bc_aws_s3_21

    Check: CKV_AWS_20: "Ensure the S3 bucket does not allow READ permissions to everyone"
            PASSED for resource: AWS::S3::Bucket.Bucket83908E77
            File: /policy-as-code.template.json:3-59
            Guide: https://docs.bridgecrew.io/docs/s3_1-acl-read-permissions-everyone

    Check: CKV_AWS_57: "Ensure the S3 bucket does not allow WRITE permissions to everyone"
            PASSED for resource: AWS::S3::Bucket.Bucket83908E77
            File: /policy-as-code.template.json:3-59
            Guide: https://docs.bridgecrew.io/docs/s3_2-acl-write-permissions-everyone

    Check: CKV_AWS_56: "Ensure S3 bucket has 'restrict_public_bucket' enabled"
            PASSED for resource: AWS::S3::Bucket.Bucket83908E77
            File: /policy-as-code.template.json:3-59
            Guide: https://docs.bridgecrew.io/docs/bc_aws_s3_22

    Check: CKV_AWS_21: "Ensure the S3 bucket has versioning enabled"
            PASSED for resource: AWS::S3::Bucket.Bucket83908E77
            File: /policy-as-code.template.json:3-59
            Guide: https://docs.bridgecrew.io/docs/s3_16-enable-versioning
    ``` 
1. Commit the changes to the repo and push to the source CodeCommit repo to kick of the pipeline.
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code/;git commit -a -m "fix checkov violations in s3_deployment.py";git push
    :::
1. View the CodePipeline in your account. Instructions to do that is [here](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-view-console.html#pipelines-list-console.). Give it about a minute to restart. Verify that the checkov rules have passed but that the cfn-guard rules are now failing. Your CodePipeline will fail on the stage **ScanDeploy** stage. Click on the **Details** on the Scan - AWS CodeBuild.
    ![ScanDeployFailed](/static/ScanDeployFailed.png)
1. You'll get a pop box that looks like below. Click on **Link to execution details**:
    ![LinkExecutionDetail](/static/LinkExecutionDetails.png)
1. The S3 deployment is running into issues with cfn-guard. The next section will look into fixing the issues and validating that S3 compliance with the cfn-guard rules.

