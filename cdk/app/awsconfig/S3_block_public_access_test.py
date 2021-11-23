# Copyright 2017-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may
# not use this file except in compliance with the License. A copy of the License is located at
#
#        http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import sys
import unittest
import json

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

##############
# Parameters #
##############

# Define the default resource to report to Config Rules
DEFAULT_RESOURCE_TYPE = 'AWS::S3::Bucket'

#############
# Main Code #
#############

CONFIG_CLIENT_MOCK = MagicMock()
STS_CLIENT_MOCK = MagicMock()
CCAPI_CLIENT_MOCK = MagicMock()

class Boto3Mock():
    @staticmethod
    def client(client_name, *args, **kwargs):
        if client_name == 'config':
            return CONFIG_CLIENT_MOCK
        if client_name == 'sts':
            return STS_CLIENT_MOCK
        if client_name == 'cloudcontrol':
            return CCAPI_CLIENT_MOCK
        raise Exception("Attempting to create an unknown client")

sys.modules['boto3'] = Boto3Mock()

RULE = __import__('S3_block_public_access')

class ComplianceTest(unittest.TestCase):

    invoking_event_bucket = '{"configurationItem":{"configurationItemStatus":"ResourceDiscovered","configurationItemCaptureTime":"2018-07-02T03:37:52.418Z","resourceType":"AWS::S3::Bucket","resourceId":"apps-us-east-1","resourceName":"apps-us-east-1"},"notificationCreationTime":"2018-07-02T23:05:34.445Z","messageType":"ConfigurationItemChangeNotification"}'
    invoking_event_bucket_compliant = '{"configurationItem":{"configurationItemStatus":"ResourceDiscovered","configurationItemCaptureTime":"2018-07-02T03:37:52.418Z","resourceType":"AWS::S3::Bucket","resourceId":"apps-test-us-east-1","resourceName":"apps-test-us-east-1"},"notificationCreationTime":"2018-07-02T23:05:34.445Z","messageType":"ConfigurationItemChangeNotification"}'

    def setUp(self):
        ccapi_mock()
    
    def test_evaluate_compliance(self):
        invoking_event = self.invoking_event_bucket
        event = build_lambda_configurationchange_event(invoking_event, '{"GUARD_FILE":"./rules/cfn-guard/s3/bucket_public_exposure.guard"}')
        configuration_item = RULE.get_configuration_item(json.loads(event['invokingEvent']))
        rule_parameters = json.loads(event['ruleParameters'])
        print(rule_parameters)
        print("configuration_item->{}".format(json.dumps(configuration_item, indent=4)))
        e = RULE.evaluate_compliance(Boto3Mock.client("cloudcontrol"), event, configuration_item, rule_parameters)
        print("e->{}".format(json.dumps(e, indent=4)))
        expected = [{'Annotation': 'deny_s3_public_access', 'ComplianceResourceType': 'AWS::S3::Bucket', 'ComplianceResourceId': 'apps-us-east-1', 'ComplianceType': 'NON_COMPLIANT', 'OrderingTimestamp': '2018-07-02T03:37:52.418Z'}]
        self.assertEqual(len(e), len(expected))
    
    def test_get_resource(self):
        invoking_event = self.invoking_event_bucket
        event = build_lambda_configurationchange_event(invoking_event, {})
        configuration_item = RULE.get_configuration_item(json.loads(event['invokingEvent']))
        r = RULE.get_resource(Boto3Mock.client("cloudcontrol"), configuration_item)
        self.assertEqual(r["ResourceDescription"]["Identifier"], json.loads(invoking_event)["configurationItem"]["resourceId"])
    
    def test_resource_to_cftemplate(self):
        invoking_event = self.invoking_event_bucket
        event = build_lambda_configurationchange_event(invoking_event, {})
        configuration_item = RULE.get_configuration_item(json.loads(event['invokingEvent']))
        r = RULE.get_resource(Boto3Mock.client("cloudcontrol"), configuration_item)
        cf_template = RULE.resource_to_cftemplate([r])
        expected = {'Resources': {'apps-us-east-1': {'Type': "AWS::S3::Bucket", 'Properties': {}}}}
        self.assertIn('apps-us-east-1', expected['Resources'])
        self.assertEqual(cf_template['Resources']['apps-us-east-1']['Type'], expected['Resources']['apps-us-east-1']['Type'])

    def test_get_file(self):
        invoking_event = self.invoking_event_bucket
        event = build_lambda_configurationchange_event(invoking_event, {})
        configuration_item = RULE.get_configuration_item(json.loads(event['invokingEvent']))
        r = RULE.get_resource(Boto3Mock.client("cloudcontrol"), configuration_item)
        cf_template = RULE.resource_to_cftemplate([r])
        with RULE.get_tempfile(json.dumps(cf_template, indent=4)) as tf:
            tf.seek(0)
            self.assertEqual(''.join(tf.readlines()), json.dumps(cf_template, indent=4))
    
    def test_cfnguard_command(self):
        invoking_event = self.invoking_event_bucket
        event = build_lambda_configurationchange_event(invoking_event, {})
        configuration_item = RULE.get_configuration_item(json.loads(event['invokingEvent']))
        r = RULE.get_resource(Boto3Mock.client("cloudcontrol"), configuration_item)
        cf_template = RULE.resource_to_cftemplate([r])
        with RULE.get_tempfile(json.dumps(cf_template, indent=4)) as tf:
            tf.seek(0)
            command = "cfn-guard validate -r {} -d {} --show-summary none -o json | jq -s '.'".format('./rules/cfn-guard/s3/bucket_public_exposure.guard', tf.name)
            output = RULE.run_process(command)
            for o in output:
                self.assertIn("status", o)

####################
# Helper Functions #
####################

def build_lambda_configurationchange_event(invoking_event, rule_parameters=None):
    event_to_return = {
        'configRuleName':'myrule',
        'executionRoleArn':'roleArn',
        'eventLeftScope': False,
        'invokingEvent': invoking_event,
        'accountId': '123456789012',
        'configRuleArn': 'arn:aws:config:us-east-1:123456789012:config-rule/config-rule-8fngan',
        'resultToken':'token'
    }
    if rule_parameters:
        event_to_return['ruleParameters'] = rule_parameters
    return event_to_return

def build_lambda_scheduled_event(rule_parameters=None):
    invoking_event = '{"messageType":"ScheduledNotification","notificationCreationTime":"2017-12-23T22:11:18.158Z"}'
    event_to_return = {
        'configRuleName':'myrule',
        'executionRoleArn':'roleArn',
        'eventLeftScope': False,
        'invokingEvent': invoking_event,
        'accountId': '123456789012',
        'configRuleArn': 'arn:aws:config:us-east-1:123456789012:config-rule/config-rule-8fngan',
        'resultToken':'token'
    }
    if rule_parameters:
        event_to_return['ruleParameters'] = rule_parameters
    return event_to_return

def build_expected_response(compliance_type, compliance_resource_id, compliance_resource_type=DEFAULT_RESOURCE_TYPE, annotation=None):
    if not annotation:
        return {
            'ComplianceType': compliance_type,
            'ComplianceResourceId': compliance_resource_id,
            'ComplianceResourceType': compliance_resource_type
            }
    return {
        'ComplianceType': compliance_type,
        'ComplianceResourceId': compliance_resource_id,
        'ComplianceResourceType': compliance_resource_type,
        'Annotation': annotation
        }

def assert_successful_evaluation(test_class, response, resp_expected, evaluations_count=1):
    if isinstance(response, dict):
        test_class.assertEquals(resp_expected['ComplianceResourceType'], response['ComplianceResourceType'])
        test_class.assertEquals(resp_expected['ComplianceResourceId'], response['ComplianceResourceId'])
        test_class.assertEquals(resp_expected['ComplianceType'], response['ComplianceType'])
        test_class.assertTrue(response['OrderingTimestamp'])
        if 'Annotation' in resp_expected or 'Annotation' in response:
            test_class.assertEquals(resp_expected['Annotation'], response['Annotation'])
    elif isinstance(response, list):
        test_class.assertEquals(evaluations_count, len(response))
        for i, response_expected in enumerate(resp_expected):
            test_class.assertEquals(response_expected['ComplianceResourceType'], response[i]['ComplianceResourceType'])
            test_class.assertEquals(response_expected['ComplianceResourceId'], response[i]['ComplianceResourceId'])
            test_class.assertEquals(response_expected['ComplianceType'], response[i]['ComplianceType'])
            test_class.assertTrue(response[i]['OrderingTimestamp'])
            if 'Annotation' in response_expected or 'Annotation' in response[i]:
                test_class.assertEquals(response_expected['Annotation'], response[i]['Annotation'])

def assert_customer_error_response(test_class, response, customer_error_code=None, customer_error_message=None):
    if customer_error_code:
        test_class.assertEqual(customer_error_code, response['customerErrorCode'])
    if customer_error_message:
        test_class.assertEqual(customer_error_message, response['customerErrorMessage'])
    test_class.assertTrue(response['customerErrorCode'])
    test_class.assertTrue(response['customerErrorMessage'])
    if "internalErrorMessage" in response:
        test_class.assertTrue(response['internalErrorMessage'])
    if "internalErrorDetails" in response:
        test_class.assertTrue(response['internalErrorDetails'])

def sts_mock():
    assume_role_response = {
        "Credentials": {
            "AccessKeyId": "string",
            "SecretAccessKey": "string",
            "SessionToken": "string"}}
    STS_CLIENT_MOCK.reset_mock(return_value=True)
    STS_CLIENT_MOCK.assume_role = MagicMock(return_value=assume_role_response)

def ccapi_mock():
    resource = {
        'TypeName': 'AWS::S3::Bucket',
        'ResourceDescription': {
            'Identifier': 'apps-us-east-1',
            'Properties': '{"PublicAccessBlockConfiguration":{"RestrictPublicBuckets":true,"BlockPublicPolicy":true,"BlockPublicAcls":false,"IgnorePublicAcls":false},"BucketName":"apps-us-east-1","RegionalDomainName":"apps-us-east-1.s3.us-east-2.amazonaws.com","DomainName":"apps-us-east-1.s3.amazonaws.com","BucketEncryption":{"ServerSideEncryptionConfiguration":[{"BucketKeyEnabled":false,"ServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]},"WebsiteURL":"http://apps-us-east-1.s3-website.us-east-2.amazonaws.com","DualStackDomainName":"apps-us-east-1.s3.dualstack.us-east-2.amazonaws.com","VersioningConfiguration":{"Status":"Enabled"},"Arn":"arn:aws:s3:::apps-us-east-1","Tags":[]}'
        },
        'ResponseMetadata': {
            'RequestId': 'a1b74ff0-ba46-4f35-937d-edff66c972a5',
            'HTTPStatusCode': 200,
            'HTTPHeaders': {
                'x-amzn-requestid': 'a1b74ff0-ba46-4f35-937d-edff66c972a5',
                'date': 'Fri, 19 Nov 2021 21:27:42 GMT',
                'content-type': 'application/x-amz-json-1.0',
                'content-length': '834'
            },
            'RetryAttempts': 0
        }
    }
    CCAPI_CLIENT_MOCK.reset_mock(return_value=True)
    CCAPI_CLIENT_MOCK.get_resource = MagicMock(return_value=resource)
