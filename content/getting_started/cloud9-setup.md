---
title: "Cloud9 Environment Setup"
weight: 31
---
This section will cover attaching the IAM instance profile to the AWS Cloud9 Environment, resizing the volume, and installing needed tools. 

1. In the AWS Console search for EC2 and click on the EC2 service:
    ![EC2 Search](/static/images/prerequisites/ec2-search.png)
    Select the Cloud9 instance. It will be named **aws-cloud9-policy-as-code-workshop-xxxxx**
    ![EC2 Select](/static/images/prerequisites/ec2-select.png)
1. Under **Actions** click on **Modify IAM role**:
    ![EC2 IAM Search](/static/images/prerequisites/ec2-modify-iamrole.png)
1. Replace **AWSCloud9SSMInstanceProfile** with **PolicyAsCodeRole** and click **Save**:
    ![EC2 IAM Role](/static/images/prerequisites/ec2-iamrole.png)
1. In the AWS Console search for Cloud9:
    ![Cloud9 Search](/static/images/prerequisites/cloud9-search.png)
    Click on the 3 horizontal bars and click on **Your environments**
    ![Cloud9 Menu](/static/images/prerequisites/cloud9-menu.png)
    You should see a Cloud9 environment named policy-as-code-workshop
    ![Cloud9 Environment](/static/images/prerequisites/cloud9-environment.png)
1. Click on **Open IDE** you should see the browser open the Cloud9 environment be patient as it may take up to 5 minutes to start:
    ![Cloud9 IDE](/static/images/prerequisites/cloud9-ide.png)
1. Disable the AWS Temporary Credentials to allow the attached role permission to resize the volume:
    Click on the gear (**preferences**) image in the top right hand corner of the Cloud9 IDE:
    ![Cloud9 Gear](/static/images/prerequisites/cloud9-gear.png)
    Click on the **AWS Settings**
    ![Cloud9 AWS Settings](/static/images/prerequisites/cloud9-aws-settings.png)
    Toggle the **AWS managed temporary credentials** to disable it as indicated by the red arrow and box:
    ![Cloud9 Disable Credentials](/static/images/prerequisites/cloud9-disable-creds.png)
1. Click on the terminal tab in Cloud9.
1. Run the following to set the region and account:
    ```bash
    sudo yum -y install jq bash-completion
    echo "export AWS_DEFAULT_REGION=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region`" >>  ~/.bash_profile
    echo "export AWS_ACCOUNT_ID=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .accountId`" >>  ~/.bash_profile
    .  ~/.bash_profile
    ```
1. Resize the Cloud9 volume by copying the following and creating a shell script called **resize.sh**:
    ```bash
    #!/bin/bash

    # Specify the desired volume size in GiB as a command line argument. If not specified, default to 20 GiB.
    SIZE=${1:-20}
    
    # Get the ID of the environment host Amazon EC2 instance.
    INSTANCEID=$(curl http://169.254.169.254/latest/meta-data/instance-id)
    REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/')
    
    # Get the ID of the Amazon EBS volume associated with the instance.
    VOLUMEID=$(aws ec2 describe-instances \
      --instance-id $INSTANCEID \
      --query "Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId" \
      --output text \
      --region $REGION)
    
    # Resize the EBS volume.
    aws ec2 modify-volume --volume-id $VOLUMEID --size $SIZE
    
    # Wait for the resize to finish.
    while [ \
      "$(aws ec2 describe-volumes-modifications \
        --volume-id $VOLUMEID \
        --filters Name=modification-state,Values="optimizing","completed" \
        --query "length(VolumesModifications)"\
        --output text)" != "1" ]; do
    sleep 1
    done
    
    #Check if we're on an NVMe filesystem
    if [[ -e "/dev/xvda" && $(readlink -f /dev/xvda) = "/dev/xvda" ]]
    then
      # Rewrite the partition table so that the partition takes up all the space that it can.
      sudo growpart /dev/xvda 1
    
      # Expand the size of the file system.
      # Check if we're on AL2
      STR=$(cat /etc/os-release)
      SUB="VERSION_ID=\"2\""
      if [[ "$STR" == *"$SUB"* ]]
      then
        sudo xfs_growfs -d /
      else
        sudo resize2fs /dev/xvda1
      fi
    
    else
      # Rewrite the partition table so that the partition takes up all the space that it can.
      sudo growpart /dev/nvme0n1 1
    
      # Expand the size of the file system.
      # Check if we're on AL2
      STR=$(cat /etc/os-release)
      SUB="VERSION_ID=\"2\""
      if [[ "$STR" == *"$SUB"* ]]
      then
        sudo xfs_growfs -d /
      else
        sudo resize2fs /dev/nvme0n1p1
      fi
    fi
    ```
1. Run the following command to increase the volume size:
    ```bash
    bash resize.sh 100
    ```
1. If your are using **Using your Own AWS Account** run the following command, skip to the next step if you are using **AWS Hosted Event** account:
    - Clone the policy-as-code repository from github in the environment directory:
      :::code{showCopyAction=true showLineNumbers=false}
      cd ~/environment;git clone https://github.com/aws-samples/policy-as-code.git
      :::
    - Install the AWS CodePipeline as follows:
      ```bash
      cd ~/environment/policy-as-code/cdk/cicd
      pip install -r requirements.txt
      cdk bootstrap
      cdk deploy --all
      ```
    - Answer 'y' to all prompts.
1. Remove **AdministratorAccess** from the IAM role **PolicyAsCodeRole**.