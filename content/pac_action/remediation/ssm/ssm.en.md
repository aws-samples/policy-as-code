---
title: "Setting up Remediation"
weight: 10
---

This section using the work done in [AWS Config Custom Rule](/pac-action/ccapi/awsconfig)

1. Find the section in the file **s3_deployment.py** with the following comments:
    ```
        # Insert Automation Role and CfnRemediationConfiguration
        # End of Automation Role and CfnRemediationConfiguration
    ``` 
1. Insert the following code snippets in between the comments:
    ```bash
            automation_assume_role = Role(self,
                                          'AutomationAssumeRole',
                                          assumed_by=ServicePrincipal(service='ssm.amazonaws.com'),
                                          managed_policies=[ ManagedPolicy.from_managed_policy_arn(self, 'AmazonSSMAutomation', 'arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole') ],
                                          inline_policies={
                                              "S3FullAccess": 
                                                  PolicyDocument(
                                                      statements=[ PolicyStatement(actions=[ "s3:*" ], resources=[ bucket.bucket_arn ]) ]
                                                  )
                                          }
            )

            CfnRemediationConfiguration(self,
                                        'AwsConfigRemdiationS3',
                                        config_rule_name=s3_config_rule.config_rule_name,
                                        target_id='AWSConfigRemediation-ConfigureS3BucketPublicAccessBlock',
                                        target_type='SSM_DOCUMENT',
                                        automatic=True,
                                        maximum_automatic_attempts=3,
                                        retry_attempt_seconds=60,
                                        parameters={
                                            'AutomationAssumeRole': {
                                                'StaticValue': {
                                                    'Values': [ automation_assume_role.role_arn ]
                                                }
                                            },
                                            'BucketName': {
                                                'ResourceValue': {
                                                    'Value': 'RESOURCE_ID'
                                                }
                                            }
                                        }
            )
    ```
1. Commit the code to the git repo:
```bash
git commit -a -m "updated to deploy remediation with SSM document"
git push
```
1. Navigate to the S3 bucket and change the permissions for the *Block public access** as specified below:
    ![S3 Public Access to fix](/static/images/prerequisites/s3-public-access-fix.png)
1. Save the changes and confirm that you want to make the changes to the S3 bucket permissions.
1. Check the AWS Config resource timeline for the S3 Bucket. It may take up to 5 minutes to complete. The remediation should fix the non-compliant S3 bucket public access permissions.
    ![S3 Public Access fixed](/static/images/prerequisites/s3-public-access-fixed.png)