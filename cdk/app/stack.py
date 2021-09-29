import aws_cdk.aws_s3
from aws_cdk import (
    core,
    aws_s3,
)


class Main(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        # sns_topic = aws_sns.Topic(
        bucket = aws_s3.Bucket(self, 'Bucket',
                               removal_policy=core.RemovalPolicy.DESTROY,
                               auto_delete_objects=True,
                               versioned=True,
                               enforce_ssl=True,
                               encryption=aws_s3.BucketEncryption.S3_MANAGED,
                               lifecycle_rules=[
                                   aws_s3.LifecycleRule(
                                       enabled=True,
                                       # expiration=core.Duration.days(90),
                                       noncurrent_version_expiration=core.Duration.days(180),
                                       abort_incomplete_multipart_upload_after=core.Duration.days(5),
                                       transitions=[aws_s3.Transition(
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
                                   block_public_acls=True,
                                   restrict_public_buckets=True,
                                   block_public_policy=True,
                                   ignore_public_acls=True

                               )
                               )
        MyDynamoDB = aws_s3.CfnAccessPoint(
            self, "AccessPoint",
            bucket=bucket.bucket_name,
            name='app1',

        )

        for i in [bucket]:
            core.Tags.of(i).add('App', 'policy-as-code')
