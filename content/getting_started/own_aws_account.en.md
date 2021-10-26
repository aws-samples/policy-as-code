---
title: "Using your Own AWS Account"
weight: 15
---
This section will cover provisioning a IAM role with the needed managed policies.

The environment needs to have the following tools installed.
1. [An AWS account](https://aws.amazon.com/getting-started/)
1. Create a IAM role named **PolicyAsCodeRole** for configuring Cloud9 instance and deploying AWS CodePipeline. 
    1. Go to the AWS Console, search for IAM in the search box and then select **IAM**.
        ![IAM Search](/static/images/prerequisites/iam-aws-console-search.png)
    1. Push the **Create role** button in the top left corner of the browser:
        ![Create role](/static/images/prerequisites/create-role.png)
    1. Select EC2 service.
        ![Select EC2 service](/static/images/prerequisites/select-ec2-service.png)
    1. Select **Next: Permissions** and select the following policies. Find the policies using the **Filter policies**:
        ![Select AdministratorAccess Policy](/static/images/prerequisites/administrator-access-policy.png)
        ![Select AWSCodeCommitPowerUser Policy](/static/images/prerequisites/codecommit-power-user.png)
        ![Select AWSCodePipeline_ReadOnlyAccess Policy](/static/images/prerequisites/codepipeline-readonly.png)
        ![Select AWSCloud9SSMInstanceProfile Policy](/static/images/prerequisites/cloud9ssm-profile.png)   
        The following AWS Managed Policies need to be attached to the role:
        * AdministratorAccess
        * AWSCodeCommitPowerUser
        * AWSCodePipeline_ReadOnlyAccess
        * AWSCloud9SSMInstanceProfile
1. Click **Next: Tags** and **Next: Review**. You should see a review screen like this:
    ![Select Review IAM Role](/static/images/prerequisites/review-iam-role.png)
    Click on **Create role**.
