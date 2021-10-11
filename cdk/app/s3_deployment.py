import aws_cdk.aws_s3
from aws_cdk import (
    core,
    aws_s3,
    aws_kms,
    aws_iam
)

class S3AppStack(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)
        
        # Insert KMS key here

        # End of KMS key here


        # Create our Bucket
        bucket = aws_s3.Bucket(self, 'Bucket',
            removal_policy=core.RemovalPolicy.DESTROY,
            auto_delete_objects=False,
            versioned=True,
            # Uncomment bucket_key_enabled=True, once the KMS key is defined
            # bucket_key_enabled=True,
            
            # Uncomment to enforce_ssl
            # enforce_ssl=True,
            
            # Once you define the KMS key uncomment encryption=aws_s3.BucketEncryption.KMS attribute
            # Remove the encryption=aws_s3.BucketEncryption.S3_MANAGED completely
            # encryption=aws_s3.BucketEncryption.KMS,
            
            # Uncommment to make checkov pass
            # encryption=aws_s3.BucketEncryption.S3_MANAGED,
            
            # Once you define the KMS key uncomment encryption_key=kms_key attribute
            # encryption_key=kms_key,
            lifecycle_rules=[
                aws_s3.LifecycleRule(
                    enabled=True,
                    # expiration=core.Duration.days(90),
                    noncurrent_version_expiration=core.Duration.days(180),
                    abort_incomplete_multipart_upload_after=core.Duration.days(5),
                    transitions=[
                        aws_s3.Transition(
                            storage_class=aws_s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=core.Duration.days(60)
                        )
                    ],
                    noncurrent_version_transitions=[
                       aws_s3.NoncurrentVersionTransition(
                           storage_class=aws_s3.StorageClass.INFREQUENT_ACCESS,
                           transition_after=core.Duration.days(31)
                       )
                    ]
                )
            ],
            block_public_access=aws_cdk.aws_s3.BlockPublicAccess(
                # Uncomment block_public_acls=True and remove block_public_acls=False
                # block_public_acls=True
                block_public_acls=False,
                restrict_public_buckets=True,
                block_public_policy=True,
                ignore_public_acls=True
            )
        )

        MyDynamoDB = aws_s3.CfnAccessPoint(
            self, "AccessPoint",
            bucket=bucket.bucket_name,
            name='app1'
        )
        
        # Insert new policy statement that denies s3:PutObject if encryption header is not set
        # End of new policy statement

        # Adds a Tag Name->App, Value->policy-as-code
        for i in [bucket]:
            core.Tags.of(i).add('App', 'policy-as-code')
