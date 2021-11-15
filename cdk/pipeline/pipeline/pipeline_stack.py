from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codecommit as codecommit,
    aws_codepipeline_actions as actions,
    aws_cloudformation as cfn,
)

props = {'namespace': 'pac'}


class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "PipelineQueue",
            visibility_timeout=Duration.seconds(300),
        )

        topic = sns.Topic(
            self, "PipelineTopic"
        )

        topic.add_subscription(subs.SqsSubscription(queue))

        # pipeline requires versioned bucket
        bucket = s3.Bucket(
            self, "SourceBucket",
            # bucket_name=f"{props['namespace'].lower()}-{core.Aws.ACCOUNT_ID}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY)

        # ssm parameter to get bucket name later
        bucket_param = ssm.StringParameter(
            self, "ParameterB",
            parameter_name=f"/{props['namespace']}/bucket",
            string_value=bucket.bucket_name,
            description='cdk pipeline bucket')

        # codebuild project meant to run in pipeline
        cb_docker_build = codebuild.PipelineProject(
            self, "DockerBuild",
            project_name=f"{props['namespace']}-cdk-synth",
            build_spec=codebuild.BuildSpec.from_source_filename(
                filename='cdk/cicd/pipeline_delivery/docker_build_buildspec.yml'),
            environment=codebuild.BuildEnvironment(
                privileged=False,
                #build_image=aws_codebuild.LinuxBuildImage.from_ecr_repository(repository=docker_asset.repository, tag=docker_asset.asset_hash)
                build_image=codebuild.LinuxBuildImage.from_docker_registry(
                    name='public.ecr.aws/f3n2w4j5/policy-as-code:latest')
            ),

            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                'tag': codebuild.BuildEnvironmentVariable(
                    value='cdk')
            },
            description='Pipeline for CodeBuild',
            timeout=Duration.minutes(15),
        )
        scan = codebuild.PipelineProject(
            self, "scan",
            project_name=f"{props['namespace']}-scan",
            build_spec=codebuild.BuildSpec.from_source_filename(
                filename='scan_buildspec.yml'),
            environment=codebuild.BuildEnvironment(
                privileged=False,
                #build_image=aws_codebuild.LinuxBuildImage.from_ecr_repository(repository=docker_asset.repository, tag=docker_asset.asset_hash)
                build_image=codebuild.LinuxBuildImage.from_docker_registry(
                    name='public.ecr.aws/f3n2w4j5/policy-as-code:latest')

            ),
            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                'tag': codebuild.BuildEnvironmentVariable(
                    value='cdk')
            },
            description='Codebuild Scan',
            timeout=Duration.minutes(15),
        )
        # repo
        # codebuild iam permissions to read write s3
        bucket.grant_read_write(cb_docker_build)

        # codebuild permissions to interact with ecr

        CfnOutput(
            self, "S3Bucket",
            description="S3 Bucket",
            value=bucket.bucket_name
        )
        # cb_docker_build.role.add_managed_policy(
        #     aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
        cb_docker_build.role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['s3:CreateBucket'],
            resources=["*"]
        )
        )

        #self.output_props = props.copy()
        #self.output_props['bucket'] = bucket
        #self.output_props['cb_docker_build'] = cb_docker_build
        #self.output_props['cb_scan'] = scan

        # define the s3 artifact
        source_output = codepipeline.Artifact(artifact_name='source')
        synth = codepipeline.Artifact(artifact_name='synth')
        scanned_source = codepipeline.Artifact(artifact_name='scanned_source')
        # define the pipeline
        repo = codecommit.Repository(
            self, "sourcerepo", repository_name='policy-as-code', description='Policy as Code Mirror')
        change_set_name = 'policy-as-code'
        pipeline = codepipeline.Pipeline(
            self, "Pipeline",
            pipeline_name=f"{props['namespace']}",
            # artifact_bucket=props['bucket'],
            artifact_bucket=bucket,
            stages=[
                codepipeline.StageProps(
                    stage_name='Source',
                    actions=[
                        # aws_codepipeline_actions.S3SourceAction(
                        #     bucket=props['bucket'],
                        #     bucket_key='source.zip',
                        #     action_name='S3Source',
                        #     run_order=1,
                        #     output=source_output,
                        #     trigger=aws_codepipeline_actions.S3Trigger.POLL
                        # ),
                        actions.CodeCommitSourceAction(
                            repository=repo,
                            action_name='source',
                            branch='main',
                            output=source_output,
                            trigger=actions.CodeCommitTrigger.EVENTS


                        )
                    ]
                ),
                codepipeline.StageProps(
                    stage_name='Build',
                    actions=[
                        actions.CodeBuildAction(
                            action_name='Synth',
                            input=source_output,
                            outputs=[synth],
                            # project=props['cb_docker_build'],
                            project=cb_docker_build,
                            run_order=1,
                        )
                    ]
                ),
                codepipeline.StageProps(
                    stage_name='ScanDeploy',
                    actions=[
                        actions.CodeBuildAction(
                            action_name='Scan',
                            input=synth,
                            # project=props['cb_scan'],
                            project=scan,
                            run_order=1,
                            outputs=[scanned_source]
                        ),
                        actions.CloudFormationCreateReplaceChangeSetAction(
                            action_name='CreateChangeSet',
                            change_set_name=change_set_name,
                            stack_name=change_set_name,
                            # input=scanned_source,
                            template_path=codepipeline.ArtifactPath(
                                artifact=scanned_source, file_name='cdk.out/policy-as-code.template.json'),
                            run_order=2,
                            cfn_capabilities=[
                                cfn.CloudFormationCapabilities.NAMED_IAM],
                            admin_permissions=True
                        ),
                        actions.CloudFormationExecuteChangeSetAction(
                            run_order=3,
                            action_name='ExecuteChangeSet',
                            change_set_name=change_set_name,
                            stack_name=change_set_name,

                        )
                    ]
                )
            ]

        )
        # give pipelinerole read write to the bucket
        # props['bucket'].grant_read_write(pipeline.role)
        bucket.grant_read_write(pipeline.role)

        # pipeline param to get the
        pipeline_param = ssm.StringParameter(
            self, "PipelineParam",
            parameter_name=f"/{props['namespace']}/pipeline",
            string_value=pipeline.pipeline_name,
            description='cdk pipeline bucket'
        )
        # cfn output
        CfnOutput(
            self, "PipelineOut",
            description="Pipeline",
            value=pipeline.pipeline_name
        )

    # pass objects to another stack
"""     @property
    def outputs(self):
        return self.output_props """
