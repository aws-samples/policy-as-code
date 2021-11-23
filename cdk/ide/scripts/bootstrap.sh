#!/bin/bash

#Add commands here to taste.
#HOME_DIR=$(cd "$(dirname "$0")/.." && pwd)
HOME_DIR="/home/ec2-user"
BIN_DIR="$HOME_DIR/bin"
ENV_DIR="$HOME_DIR/environment"
TMP_DIR="$HOME_DIR/tmp"

#Set environment variables
sudo yum -y install jq bash-completion
echo "export AWS_DEFAULT_REGION=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region`" >>  $HOME_DIR/.bash_profile
echo "export AWS_ACCOUNT_ID=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .accountId`" >>  $HOME_DIR/.bash_profile
#.  $HOME_DIR/.bash_profile
source $HOME_DIR/.bash_profile

# Make directory for tools
mkdir -p $BIN_DIR
mkdir -p $TMP_DIR

#Clone the workshop repo
cd $ENV_DIR;git clone https://github.com/aws-samples/policy-as-code.git

#Install Rust and Cargo
cd $HOME_DIR
curl https://sh.rustup.rs -sSf | sh -s -- -y
source $HOME_DIR/.cargo/env

#Install cfn-guard
# Latest official build - via Cargo
#~/.cargo/bin/cargo install cfn-guard 

#Latest official build - download and install
#$ curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/aws-cloudformation/cloudformation-guard/main/install-guard.sh | sh

# Beta / RC build
cd $TMP_DIR
# Binary - doesn't currently work on Amazon Linux 2 - fails with gclib version error
#wget https://github.com/aws-cloudformation/cloudformation-guard/releases/download/v2.1.0-pre-rc1/cfn-guard-v2-ubuntu-latest.tar.gz

# Build from source - slower. but works on Amazon Linux 2
wget https://github.com/aws-cloudformation/cloudformation-guard/archive/refs/tags/v2.1.0-pre-rc1.zip
unzip v2.1.0-pre-rc1.zip
cd cloudformation-guard-2.1.0-pre-rc1/
cd cfn-guard-v2-ubuntu-latest 
RUSTFLAGS=-Awarnings ~/.cargo/bin/cargo build --release
cp ./target/release/cfn-guard $BIN_DIR
#cfn-guard --version


# Configure Python virtual environment 
cd $HOME_DIR
python3 -m venv .env
source .env/bin/activate

#Install Checkov
pip3 install checkov

#Install Open Policy Agent CLI
cd $BIN_DIR && curl -L -o opa https://openpolicyagent.org/downloads/v0.34.2/opa_linux_amd64_static && chmod 755 ./opa

#Install Regula
cd $TMP_DIR
wget https://github.com/fugue/regula/releases/download/v1.6.0/regula_1.6.0_Linux_x86_64.tar.gz
tar xvzf regula_1.6.0_Linux_x86_64.tar.gz -C $BIN_DIR regula

#Install cfn-lint
pip install cfn-lint

# Install NodeJS and NPM
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source $HOME_DIR/.bashrc
source $HOME_DIR/.bash_profile

# Install CDK v1
$BIN_DIR/npm install -g aws-cdk
#cdk --version
source $HOME_DIR/.bashrc
source $HOME_DIR/.bash_profile

# Deploy the pipeline for student exercises
cd $HOME_DIR/environment/policy-as-code/cdk/cicd
pip install -r requirements.txt
cdk bootstrap
cdk deploy --all --require-approval never

#Examples of pulling 
#aws s3 cp s3://ee-assets-prod-us-east-1/modules/2a60741f901644fa9b5b924e9b4ab918/v1/scripts/init.js /home/ec2-user/environment/.c9/metadata/environment/~/.c9/init.js
#chown ec2-user:ec2-user /home/ec2-user/environment/.c9/metadata/environment/~/.c9/init.js

#aws s3 cp s3://ee-assets-prod-us-east-1/modules/2a60741f901644fa9b5b924e9b4ab918/v1/scripts/envsetup.sh /home/ec2-user/environment/envsetup.sh
#chown ec2-user:ec2-user /home/ec2-user/environment/envsetup.sh
