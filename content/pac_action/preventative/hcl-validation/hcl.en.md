---
title: "Terraform HCL Validation"
weight: 10
---

The S3 application is ready to be deployed. In order for it to be deployed successfully it must comply with the rules created as specified above.
To kickoff the deployment use git push to AWS CodeCommit which is the source for the pipeline. During this workshop the Terraform HCL code will be
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
