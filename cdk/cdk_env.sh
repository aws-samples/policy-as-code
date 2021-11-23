# Set CDK environment variables to current AWS credentials and region
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity | jq -r .Account)
export CDK_DEFAULT_REGION=$(aws configure get region)
export AWS_REGION=$CDK_DEFAULT_REGION
export AWS_ACCOUNT_ID=$CDK_DEFAULT_ACCOUNT

echo "CDK_DEFAULT_ACCOUNT=$CDK_DEFAULT_ACCOUNT"
echo "CDK_DEFAULT_REGION=$CDK_DEFAULT_REGION"
echo "AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID"
echo "AWS_REGION=$AWS_REGION"
