import json
import pytest

import aws_cdk_lib as core
from pipeline.pipeline_stack import PipelineStack


def get_template():
    app = core.App()
    PipelineStack(app, "pipeline")
    return json.dumps(app.synth().get_stack("pipeline").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
