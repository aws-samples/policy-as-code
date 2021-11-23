---
title: "Using Cloud Control API with cfn-guard"
weight: 10
---

This section will explore the output of the AWS Cloud Control API as well as how to validate resource against the cfn-guard policies that were created in the section [AWS CDK and Cloudformation](/policy-as-code-action/preventative/cfn-validation):

1. Make sure you are using aws correct version:
    ```bash
    aws --version
    ``` 
    You should be on a version 2.3.6+ or higher.
1. Issue the following for the name of the S3 bucket from the previous section of this workshop:
    ```bash
    aws cloudcontrol get-resource --type-name "AWS::S3::Bucket" --identifier "<Replace with the name of the S3 bucket>"
    ```
    The output will look something like this:
    ```
    {
        "TypeName": "AWS::S3::Bucket",
        "ResourceDescription": {
            "Identifier": "policy-as-code-294124263825",
            "Properties": "{\"PublicAccessBlockConfiguration\":{\"RestrictPublicBuckets\":true,\"BlockPublicPolicy\":true,\"BlockPublicAcls\":false,\"IgnorePublicAcls\":false},\"BucketName\":\"policy-as-code-294124263825\",\"RegionalDomainName\":\"policy-as-code-294124263825.s3.us-east-2.amazonaws.com\",\"DomainName\":\"policy-as-code-294124263825.s3.amazonaws.com\",\"BucketEncryption\":{\"ServerSideEncryptionConfiguration\":[{\"BucketKeyEnabled\":false,\"ServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"AES256\"}}]},\"WebsiteURL\":\"http://policy-as-code-294124263825.s3-website.us-east-2.amazonaws.com\",\"DualStackDomainName\":\"policy-as-code-294124263825.s3.dualstack.us-east-2.amazonaws.com\",\"VersioningConfiguration\":{\"Status\":\"Enabled\"},\"Arn\":\"arn:aws:s3:::policy-as-code-294124263825\",\"Tags\":[]}"
        }
    }
    ```
    Note: the **"Properties"** attribute might wrap differently on your terminal.
1. Observe that the **"Properties"** attribute contains a string that is formatted as JSON. The properties match the **"Properties"** syntax for the CloudFormation syntax [AWS::S3::Bucket](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html).
1. Using the utility jq the output can be converted to a CloudFormation style resource. Do the following:
    ```bash
    cd ~/environment/policy-as-code/cdk/app
    aws cloudcontrol get-resource --type-name "AWS::S3::Bucket" --identifier <Replace with name of the S3 Bucket> | jq '. | {Resources: {(.ResourceDescription.Identifier): {Type: .TypeName, Properties: .ResourceDescription.Properties | fromjson}}}' > s3-cfn.json
    ```
1. There should be a file in the current directory named **s3-cfn.json**. It should now be possible to validate this AWS resource against the cfn-guard rules. Do the following:
    ```bash
    cfn-guard validate -r rules/cfn-guard/s3/bucket_public_exposure.guard -d s3-cfn.json --show-summary all
    ```
    The output should look something like this:
    ```
    s3-cfn.json Status = PASS
    PASS rules
    bucket_public_exposure.guard/deny_s3_access_control           PASS
    bucket_public_exposure.guard/deny_s3_notification_settings    PASS
    bucket_public_exposure.guard/deny_s3_cors_settings            PASS
    bucket_public_exposure.guard/deny_s3_website_configuration    PASS
    bucket_public_exposure.guard/deny_s3_public_access            PASS
    ```
    In the next section the workflow described here will be used to create an AWS Config Custom rule that will validate the cfn-guard policy when the S3 bucket public access is modified.
