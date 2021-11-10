import json
import urllib.parse
import boto3
import logging
import traceback
import cfnresponse
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    logger.debug('Event: {}'.format(event))
    logger.debug('Context: {}'.format(context))

    # init response
    props = event
    response_status = cfnresponse.FAILED
    response_data = {}

    # Immediately respond on Delete
    if event['RequestType'] == 'Delete':
        try:
            logger.debug('Event: {}'.format(event))
            cfnresponse.send(event, context, cfnresponse.SUCCESS,
                             responseData, 'CustomResourcePhysicalID')
        except Exception as e:
            logger.error(e, exc_info=True)
            responseData = {'Error': traceback.format_exc(e)}
            cfnresponse.send(event, context, cfnresponse.FAILED,
                             responseData, 'CustomResourcePhysicalID')

    if event['RequestType'] == 'Create':
        try:
            # Open AWS clients
            ec2 = boto3.client('ec2')

            # Get the Instance object from the InstanceId
            instance = ec2.describe_instances(Filters=[
                                              {'Name': 'instance-id', 'Values': [props['InstanceId']]}])['Reservations'][0]['Instances'][0]
            instanceId = instance['InstanceId']

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

            responseData = {
                'Success': 'Role added to instance'+instance['InstanceId']+'.'}
            cfnresponse.send(event, context, cfnresponse.SUCCESS,
                             responseData, 'CustomResourcePhysicalID')
        except Exception as e:
            logger.error(e, exc_info=True)
            responseData = {'Error': traceback.format_exc(e)}
            cfnresponse.send(event, context, cfnresponse.FAILED,
                             responseData, 'CustomResourcePhysicalID')
