from aws_cdk import (
    App,
    Environment,
)
import os
import pathlib
from s3_deployment import S3AppStack

app = App()

S3AppStack(app, "policy-as-code",
           env=Environment(
               account=os.environ["CDK_DEFAULT_ACCOUNT"],
               region=os.environ["CDK_DEFAULT_REGION"]
           ),
           description='')

app.synth()
