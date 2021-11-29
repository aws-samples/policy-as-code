---
title: "Terraform HCL Validation"
weight: 10
---

The S3 application is ready to be deployed. In order for it to be deployed successfully it must comply with the rules created as specified above.
To kickoff the deployment use git push to AWS CodeCommit which is the source for the pipeline. During this workshop the Terraform HCL code will be
changed to comply with the rules specified in the AWS CodePipeline. Do the following:

1. Install the AWS CodePipeline as follows:
    ```bash
    cd ~/environment/policy-as-code/terraform/cicd
    pip install -r requirements.txt
    cdk bootstrap
    cdk deploy --all --require-approval never
    ```
    ::alert[Wait for the cdk deployment to finish before going on to the next step.]
1. Once the cdk deployment is completed, remove the reference to the upstream code repo by issuing the command:
    ```bash
    git remote remove origin
    ```
1. Get the repository clone URL by running the the following commands and adding it as our remote origin:
    ```bash
    export repo=$(aws codecommit list-repositories --output text | awk '{print $3}' | grep policy-as-code)
    export codecommiturl=$(aws codecommit get-repository --repository-name ${repo} --query 'repositoryMetadata.cloneUrlHttp' --output text)
    git remote add origin ${codecommiturl}
    ```
1. Make sure that you have the git-remote-codecommit python package installed. This helps with authenticating with CodeCommit.
    ```bash
    pip install git-remote-codecommit
    ```
1. Push the repo by issue the command: 
    ```bash
    git push --set-upstream origin main
    ```

