#!/bin/bash

#Add commands here to taste.

#Set environment variables
sudo yum -y install jq bash-completion
echo "export AWS_DEFAULT_REGION=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region`" >>  ~/.bash_profile
echo "export AWS_ACCOUNT_ID=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .accountId`" >>  ~/.bash_profile
.  ~/.bash_profile

#Clone the workshop repo
cd ~/environment;git clone https://github.com/aws-samples/policy-as-code.git

#Install Rust and Cargo
curl https://sh.rustup.rs -sSf | sh -s -- -y
source $HOME/.cargo/env

#Install cfn-guard
cargo install cfn-guard
$ curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/aws-cloudformation/cloudformation-guard/main/install-guard.sh | sh

#Install Checkov
pip3 install checkov

#Install Open Policy Agent CLI
cd ~ && curl -L -o opa https://openpolicyagent.org/downloads/v0.34.2/opa_linux_amd64_static && chmod 755 ./opa

#Install Regula
wget https://github.com/fugue/regula/releases/download/v1.6.0/regula_1.6.0_Linux_x86_64.tar.gz
mkdir ~/bin && tar xvzf regula_1.6.0_Linux_x86_64.tar.gz -C ~/bin regula

#Install cfn-lint
pip install cfn-lint

#Examples of pulling 
#aws s3 cp s3://ee-assets-prod-us-east-1/modules/2a60741f901644fa9b5b924e9b4ab918/v1/scripts/init.js /home/ec2-user/environment/.c9/metadata/environment/~/.c9/init.js
#chown ec2-user:ec2-user /home/ec2-user/environment/.c9/metadata/environment/~/.c9/init.js

#aws s3 cp s3://ee-assets-prod-us-east-1/modules/2a60741f901644fa9b5b924e9b4ab918/v1/scripts/envsetup.sh /home/ec2-user/environment/envsetup.sh
#chown ec2-user:ec2-user /home/ec2-user/environment/envsetup.sh
