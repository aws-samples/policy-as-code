---
title: "CloudFormation Validation"
weight: 20
---

The S3 application is ready to be deployed. In order for it to be deployed successfully it must comply with the rules created as specified above.
To kickoff the deployment use git push to AWS CodeCommit which is the source for the pipeline. During this workshop the CDK/CFN template will be
changed to comply with the rules specified in the AWS CodePipeline. Do the following:

1. Clone the workshop repo (If this is not already done.):
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code
    :::
1. Remove the reference to the upstream code repo by issuing the command:
    :::code{showCopyAction=true showLineNumbers=false}
    git remote remove origin
    :::
1. Get the repository clone URL by running the the following commands and adding it as our remote origin:
    ```
    export repo=$(aws codecommit list-repositories --output text | awk '{print $3}' | grep policy-as-code)
    export codecommiturl=$(aws codecommit get-repository --repository-name ${repo} --query 'repositoryMetadata.cloneUrlHttp'    --output text)
    git remote add origin ${codecommiturl}
    ```
1. Make sure that you have the git-remote-codecommit python package installed. This helps with authenticating with CodeCommit.
    :::code{showCopyAction=true}
    pip install git-remote-codecommit
    :::
1. Push the repo
    :::code{showCopyAction=true showLineNumbers=false}
    git push --set-upstream origin main
    :::
1. View the CodePipeline in your account. Instructions to do that is [here](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-view-console.html#pipelines-list-console.). Give it about a minute to restart. Initially the Pipeline will have failed because when deployed for the first time there was nothing in the CodeCommit repo.
1. Your CodePipeline will fail on the stage **ScanDeploy** stage. Click on the **Details** on the Scan - AWS CodeBuild.
    ![ScanDeployFailed](/static/ScanDeployFailed.png)
1. You'll get a pop box that looks like below. Click on **Link to execution details**:
    ![LinkExecutionDetail](/static/LinkExecutionDetails.png)
1. This should bring you to the CodeBuild project. The two failures look like this:
    ```
    Check: CKV_AWS_53: "Ensure S3 bucket has block public ACLS enabled"
        FAILED for resource: AWS::S3::Bucket.Bucket83908E77
        File: /policy-as-code.template.json:3-50
        Guide: https://docs.bridgecrew.io/docs/bc_aws_s3_19

            3  |     "Bucket83908E77": {
            4  |       "Type": "AWS::S3::Bucket",
            5  |       "Properties": {
    ...
            29 |         "PublicAccessBlockConfiguration": {
            30 |           "BlockPublicAcls": false,
            31 |           "BlockPublicPolicy": true,
            32 |           "IgnorePublicAcls": true,
            33 |           "RestrictPublicBuckets": true
    ```
    ```
    Check: CKV_AWS_19: "Ensure the S3 bucket has server-side-encryption enabled"
        FAILED for resource: AWS::S3::Bucket.Bucket83908E77
        File: /policy-as-code.template.json:3-50
        Guide: https://docs.bridgecrew.io/docs/s3_14-data-encrypted-at-rest

            3  |     "Bucket83908E77": {
            4  |       "Type": "AWS::S3::Bucket",
            5  |       "Properties": {
    ```
1. The S3 deployment is running into issues with checkov. The next section will look into fixing the issues and validating that S3 compliance with the checkov rules.

