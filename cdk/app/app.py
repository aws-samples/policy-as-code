from aws_cdk import (
    core
)
import os
import pathlib
from stack import Main
env = core.Environment(account='805159726499', region="us-east-1")
app = core.App()
Main(app, "policy-as-code", env=env, description='Peloton Notifier')

app.synth()
