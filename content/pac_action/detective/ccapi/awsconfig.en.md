---
title: "AWS Config Custom Rule"
weight: 12
---

This section will explore using AWS CC API, cfn-guard, and the AWS Config Custom Rule to provide a detective control for the S3 deployment. Using what was learned in [CC API and cfn-guard](/pac-action/detective/ccapi/ccapi).

1. Enable AWS Config by navigating to the AWS Config service page and click on the button **1-click setup**:
    ![AWSConfigServicePage.png](/static/AWSConfigServicePage.png)
1. Click on the button **Confirm**
    ![AWSConfigConfirm.png](/static/AWSConfigConfirm.png)
1. When successful you should see the AWS Config Dashboard:
    ![AWSConfigDashboard.png](/static/AWSConfigDashboard.png)
1. Go back to the Cloud9 instance and validate the following directory:
    ```bash
    cd ~/environment/policy-as-code/cdk/app
    ls awsconfig
    ```
    It should have an output like:
    ```
    total 16560
    -rw-r--r--  1 johnyi  staff      367 Nov 23 11:53 Dockerfile
    -rw-r--r--  1 johnyi  staff    19483 Nov 23 11:53 S3_block_public_access.py
    -rw-r--r--  1 johnyi  staff    11389 Nov 23 11:53 S3_block_public_access_test.py
    -rwxr-xr-x@ 1 johnyi  staff  8431728 Nov 20 23:49 cfn-guard
    -rw-r--r--  1 johnyi  staff      282 Nov 23 11:53 parameters.json
    -rw-r--r--  1 johnyi  staff       15 Nov 23 11:53 requirements.txt
    drwxr-xr-x  4 johnyi  staff      128 Nov 23 11:53 rules
    ```
    The **rules** directory is a copy of the rules directory in the ~/environment/policy-as-code/cdk/app. This will be deployed along with the AWS Lambda function that will be the core of the AWS Config Custom Rule.
1. The **s3_deployment.py** CDK application will need to create a AWS Lambda function based on the Docker image in the directory awsconfig. Find the following lines:
    ```
    ...
    # Insert AWS Lambda Function for Custom AWS Config rule
    # End of AWS Lambda Function
    ...
    ```
    Insert the folling code snippet to define our AWS Lambda function inside the comments:
    ```python
            aws_config_fn = DockerImageFunction(self, 'AwsConfigFn', code=DockerImageCode.from_image_asset(directory=os.path.join(os.path.curdir, 'awsconfig')), timeout=Duration.minutes(3))
            aws_config_fn.add_to_role_policy(
                PolicyStatement(
                    sid="CloudControlAPIReadOnlyAccess",
                    actions=[
                        "cloudformation:ListResources",
                        "cloudformation:GetResource"
                    ],
                    resources=[
                        "*"
                    ]
                )
            )

            aws_config_fn.add_to_role_policy(
                PolicyStatement(
                    sid="AWSConfigBucketPermissionsCheck",
                    actions=[
                        "s3:Get*",
                        "s3:ListBucket"
                    ],
                    resources=[
                        bucket.bucket_arn
                    ]
                )
            )
    ```
1. Now define the AWS Config Custom Rule by finding the comments in **s3_deployment.py**:
    ```
    # Insert AWS Config Custom Rule
    # End of AWS Config Custom Rule
    ```
    Insert the code snippet:
    ```python
            s3_config_rule = CustomRule(self,
                                        'AwsConfigRuleS3',
                                        config_rule_name='S3PublicAccessSettings',
                                        input_parameters={
                                            "GUARD_FILE": "./rules/cfn-guard/s3/bucket_public_exposure.guard" # Config Rule that checks for S3 Public exposure
                                        },
                                        lambda_function=aws_config_fn,
                                        configuration_changes=True,
                                        rule_scope=RuleScope.from_resource(ResourceType.S3_BUCKET, bucket.bucket_name)
            )
    ```
1. The pasted code in the **s3_deployment.py** should look something like this:
    ```
        ...
        # Insert AWS Lambda Function for Custom AWS Config rule
        aws_config_fn = DockerImageFunction(self, 'AwsConfigFn', code=DockerImageCode.from_image_asset(directory=os.path.join(os.path.curdir, 'awsconfig')), timeout=Duration.minutes(3))
        aws_config_fn.add_to_role_policy(
            PolicyStatement(
                sid="CloudControlAPIReadOnlyAccess",
                actions=[
                    "cloudformation:ListResources",
                    "cloudformation:GetResource"
                ],
                resources=[
                    "*"
                ]
            )
        )

        aws_config_fn.add_to_role_policy(
            PolicyStatement(
                sid="AWSConfigBucketPermissionsCheck",
                actions=[
                    "s3:Get*",
                    "s3:ListBucket"
                ],
                resources=[
                    bucket.bucket_arn
                ]
            )
        )
        # End of AWS Lambda Function

        # Insert AWS Config Custom Rule
        s3_config_rule = CustomRule(self,
                                    'AwsConfigRuleS3',
                                    config_rule_name='S3PublicAccessSettings',
                                    input_parameters={
                                        "GUARD_FILE": "./rules/cfn-guard/s3/bucket_public_exposure.guard" # Config Rule that checks for S3 Public exposure
                                    },
                                    lambda_function=aws_config_fn,
                                    configuration_changes=True,
                                    rule_scope=RuleScope.from_resource(ResourceType.S3_BUCKET, bucket.bucket_name)
        )
        # End of AWS Config Custom Rule
        ...
    ```
1. The AWS Config Custom Rule is ready to be deployed. Do the following:
    ```bash
    cd ~/environment/policy-as-code/cdk/app
    cdk deploy --require-approval never
    ```
1. If this is successfully you should see the output similiar to this:
    ![AWSConfig Deploy](/static/images/prerequisites/awsconfig-deploy-success.png)

    Also the command:
    ```bash
    aws configservice describe-config-rules --query 'ConfigRules[?ConfigRuleName==`S3PublicAccessSettings`]'
    ```

    Should return a JSON object.
1. Look for an S3 bucket with a name like **policy-as-code-bucket** in the S3 console page.
1. Once the config rule has been succesfully deployed a policy violation needs to be simulated. Do that by changing the permission of the S3 Bucket. Navigate to the S3 service and click on the **Permissions** tab:
    ![S3 Bucket Permissions](/static/images/prerequisites/s3-bucket-permissions.png)
1. Change the **Block public access to buckets and objects granted through new access control lists (ACLs)** to be false as shown below:
    ![S3 Bucket ACL False](/static/images/prerequisites/s3-bucket-acl-false.png)
    Make sure to save the changes by clicking on **Save changes** button. Confirm the update by typing in **confirm**:
    ![S3 Edit public access confirm](/static/images/prerequisites/s3-edit-public-access-confirm.png)
    When done it should look like below:
    ![S3 public access updated](/static/images/prerequisites/s3-public-access-updated.png)
1. Navigate to AWS Config and click on **Resources**. Use the filter for **Resource type** and select **AWS::S3::Bucket**:
    ![AWS Config Resource Filter](/static/images/prerequisites/aws-config-resource-filter.png)
    Find the S3 bucket that the pipeline deployed and click on it:
    ![AWS Config S3 Resource](/static/images/prerequisites/aws-config-s3-resource.png)
1. Click on the **Resource Timeline**. It will display the configuration change that caused the config rule to be non-compliant:
    ![AWS Config Timeline 1](/static/images/prerequisites/aws-config-timeline-1.png)
    ![AWS Config Timeline 2](/static/images/prerequisites/aws-config-timeline-2.png)
    If this does not appear wait, it may take up to 5 minutes to be updated.

The next section will explore [remediating noncompliant](https://docs.aws.amazon.com/config/latest/developerguide/remediation.html) resources using [AWS Systems Manager Automation documents](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html).