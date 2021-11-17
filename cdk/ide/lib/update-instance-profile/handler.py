from __future__ import print_function
from crhelper import CfnResource
import json
import boto3
import logging
import time

helper = CfnResource()

logger = logging.getLogger(__name__)
# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG',
                     boto_level='CRITICAL', sleep_on_delete=120, ssl_verify=None)

try:
    #ec2_client = boto3.client('ec2')
    ssm_client = boto3.client('ssm')
except Exception as e:
    helper.init_failure(e)


@helper.create
@helper.update
def lambda_handler(event, context):
    try:
        props = event['ResourceProperties']

        # Open AWS clients
        ec2 = boto3.client('ec2')

        # Get the Instance object from the InstanceId
        instance = ec2.describe_instances(Filters=[
            {'Name': 'instance-id', 'Values': [props['InstanceId']]}])['Reservations'][0]['Instances'][0]
        instanceId = instance['InstanceId']

        while not ssm_ready(instanceId):
            if context.get_remaining_time_in_millis() < 20000:
                raise Exception(
                    "Timed out waiting for instance to register with SSM")
            time.sleep(15)

        # Create the IamInstanceProfile request object
        iam_instance_profile = {
            'Arn': props['InstanceProfileArn']
        }

        # Wait for Instance to become ready before adding Role
        instance_state = instance['State']['Name']
        while instance_state != 'running':
            time.sleep(5)
            instance_state = ec2.describe_instances(
                InstanceIds=[instance['InstanceId']])
        if 'IamInstanceProfile' in instance:
            association_id = ec2.describe_iam_instance_profile_associations(
                Filters=[{'Name': 'instance-id', 'Values': [instance['InstanceId']]}])['IamInstanceProfileAssociations'][0]['AssociationId']
            ec2.replace_iam_instance_profile_association(
                IamInstanceProfile=iam_instance_profile, AssociationId=association_id)
        else:
            ec2.associate_iam_instance_profile(
                IamInstanceProfile=iam_instance_profile, InstanceId=instance['InstanceId'])
    except Exception as e:
        logger.error(e, exc_info=True)
        raise ValueError(f"Problem updating instance profile: {e}")


@helper.delete
def no_op(_, __):
    pass


def ssm_ready(instance_id):
    try:
        response = ssm_client.describe_instance_information(Filters=[
            {'Key': 'InstanceIds', 'Values': [instance_id]}
        ])
        logger.debug(response)
        return True
    except ssm_client.exceptions.InvalidInstanceId:
        return False


def handler(event, context):
    helper(event, context)
