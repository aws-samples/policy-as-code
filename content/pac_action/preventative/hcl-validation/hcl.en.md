---
title: "Terraform HCL Validation"
weight: 10
---

The S3 application is ready to be deployed. In order for it to be deployed successfully it must comply with the rules created as specified above.
To kickoff the deployment use git push to AWS CodeCommit which is the source for the pipeline. During this workshop the Terraform HCL code will be
changed to comply with the rules specified in the AWS CodePipeline. Do the following:
1. Make sure the steps in [Installing the Tools and the AWS CodePipeline](/getting-started/tool-installation) has been completed before continuing with this section.
1. Push the repo by issue the command: 
    ```bash
    git push --set-upstream origin main
    ```
1. Modify the buildspec file to use terraform to deploy the S3 application:
    ```bash
    
    ```
