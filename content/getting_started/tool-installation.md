---
title: "Installing the Tools and the AWS CodePipeline"
weight: 40
---

This section will cover the installation of the tools needed to run through this workshop as well as the deployment of the AWS CodePipeline.

1. Install the command line tools by running these commands:
    ```bash
    cd ~/environment/policy-as-code
    source ./cdk/ide/scripts/bootstrap.sh
    ```
1. Install the AWS CodePipeline as follows:
    ```bash
    cd ~/environment/policy-as-code/cdk/cicd
    pip install -r requirements.txt
    cdk bootstrap
    cdk deploy --all --require-approval never
    ```
    cdk will prompty for a yes or no, answer 'y' to all prompts.
    ::alert[Wait for the cdk deployment to finish before going on to the next step.]
1. Once the cdk deployment is completed, remove the reference to the upstream code repo by issuing the command:
    :::code{showCopyAction=true showLineNumbers=false}
    git remote remove origin
    :::
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
