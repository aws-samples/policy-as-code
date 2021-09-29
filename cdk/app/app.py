from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_lambda_destinations,
    aws_sns,
    aws_ssm,
    aws_iam,
    aws_s3,
    aws_sns_subscriptions,
    aws_events_targets as targets,
    core,
    aws_logs,
)
import os
import pathlib
from stack import Main
env = core.Environment(account='805159726499', region="us-east-1")
app = core.App()
Main(app, "policy-as-code", env=env, description='Peloton Notifier')

app.synth()
