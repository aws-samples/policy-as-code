#!/usr/bin/env python3

import aws_cdk as cdk

from pipeline.pipeline_stack import PipelineStack


app = cdk.App()
PipelineStack(app, "pipeline")

app.synth()
