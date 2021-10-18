---
title: "Cleanup"
weight: 50
---

1. Attach the AWS Managed IAM policy AdministratorAccess to the IAM role **PolicyAsCodeRole**.
1. Change directory to the S3 CDK application:
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code/cdk/app
    :::
1. Destroy the S3 CDK application by running:
    :::code{showCopyAction=true showLineNumbers=false}
    cdk destroy --all
    :::
    Answer 'y' to any prompts.
1. Change directory to the CodePipeline CDK application:
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code/cdk/cicd
    :::
1. Remove pac-base S3 bucket.
    ```
    export s3_bucket=$(aws s3 ls | grep 'pac-base-sourcebucket' | awk '{print $3}')
    aws s3 rm --recursive s3://${s3_bucket}
    aws s3 rb --force s3://${s3_bucket}
    ```
1. Destroy the CodePipeline CDK application:
    :::code{showCopyAction=true showLineNumbers=false}
    cdk destroy --all
    :::
    Answer 'y' to all prompts.
1. Exit out of Cloud9.
1. In the AWS Console, delete the [Cloud9 environment](https://docs.aws.amazon.com/cloud9/latest/user-guide/delete-environment.html)