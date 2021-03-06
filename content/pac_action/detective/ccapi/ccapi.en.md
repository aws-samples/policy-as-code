---
title: "CC API and cfn-guard"
weight: 10
---

This section will explore the output of the AWS Cloud Control API as well as how to validate resource against the cfn-guard policies that were created in the section [AWS CDK and Cloudformation](/policy-as-code-action/preventative/cfn-validation):

1. Make sure you are using aws correct version:
    ```bash
    aws --version
    ``` 
    You should be on a version 2.3.6+ or higher.
1. Locate the S3 bucket deployed by the pipeline by issue the following command:
    ```bash
    aws s3 ls
    ```
    Look for a bucket with the pattern **policy-as-code-bucketxxxx-xxx**
1. Issue the following for the name of the S3 bucket from the previous section of this workshop:
    ```bash
    aws cloudcontrol get-resource --type-name "AWS::S3::Bucket" --identifier "<Replace with the name policy-as-code-bucketxxxx-xxx>"
    ```
    The output will look something like this:
    ```
    {
        "TypeName": "AWS::S3::Bucket",
        "ResourceDescription": {
            "Identifier": "policy-as-code-bucket83908e77-1hoazld23kjrb",
            "Properties": "{\"PublicAccessBlockConfiguration\":{\"RestrictPublicBuckets\":true,\"BlockPublicPolicy\":true,\"BlockPublicAcls\":true,\"IgnorePublicAcls\":true},\"BucketName\":\"policy-as-code-bucket83908e77-1hoazld23kjrb\",\"RegionalDomainName\":\"policy-as-code-bucket83908e77-1hoazld23kjrb.s3.us-east-2.amazonaws.com\",\"DomainName\":\"policy-as-code-bucket83908e77-1hoazld23kjrb.s3.amazonaws.com\",\"WebsiteURL\":\"http://policy-as-code-bucket83908e77-1hoazld23kjrb.s3-website.us-east-2.amazonaws.com\",\"LifecycleConfiguration\":{\"Rules\":[{\"Status\":\"Enabled\",\"NoncurrentVersionTransition\":{\"StorageClass\":\"STANDARD_IA\",\"TransitionInDays\":31},\"NoncurrentVersionExpirationInDays\":180,\"TagFilters\":[null],\"Transition\":{\"StorageClass\":\"STANDARD_IA\",\"TransitionInDays\":60},\"NoncurrentVersionTransitions\":[],\"Id\":\"ZmQxMTA3N2MtZjYyMS00MTQ2LThmYmYtYzY3OWFiY2UwMzVi\",\"Prefix\":\"\",\"AbortIncompleteMultipartUpload\":{\"DaysAfterInitiation\":5}}]},\"DualStackDomainName\":\"policy-as-code-bucket83908e77-1hoazld23kjrb.s3.dualstack.us-east-2.amazonaws.com\",\"VersioningConfiguration\":{\"Status\":\"Enabled\"},\"Arn\":\"arn:aws:s3:::policy-as-code-bucket83908e77-1hoazld23kjrb\",\"Tags\":[{\"Value\":\"policy-as-code\",\"Key\":\"App\"}]}"
        }
    }
    ```
    Note: the **"Properties"** attribute might wrap differently on your terminal.
1. Observe that the **"Properties"** attribute contains a string that is formatted as JSON. The properties match the **"Properties"** syntax for the CloudFormation syntax [AWS::S3::Bucket](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html).
1. Using the utility jq the output can be converted to a CloudFormation style resource. Do the following:
    ```bash
    cd ~/environment/policy-as-code/cdk/app
    aws cloudcontrol get-resource --type-name "AWS::S3::Bucket" --identifier <Replace with the name policy-as-code-bucketxxxx-xxx> | jq '. | {Resources: {(.ResourceDescription.Identifier): {Type: .TypeName, Properties: .ResourceDescription.Properties | fromjson}}}' > s3-cfn.json
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
