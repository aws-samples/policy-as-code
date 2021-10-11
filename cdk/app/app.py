from aws_cdk import (
    core
)
import os
import pathlib
from s3_deployment import S3AppStack

app = core.App()

S3AppStack(app, "policy-as-code",
    env=core.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"]
    ),
    description='')

app.synth()
