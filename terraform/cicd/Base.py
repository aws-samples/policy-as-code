import aws_cdk.aws_codebuild
from aws_cdk import (
    aws_s3 as aws_s3,
    aws_ecr,
    aws_codebuild,
    aws_codecommit,
    aws_ssm,
    aws_iam,
    core,
    aws_ecr_assets
)


class Base(core.Stack):
    def __init__(self, app: core.App, id: str, props, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # pipeline requires versioned bucket
        bucket = aws_s3.Bucket(
            self, "SourceBucket",
            #bucket_name=f"{props['namespace'].lower()}-{core.Aws.ACCOUNT_ID}",
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY)
        # ssm parameter to get bucket name later
        bucket_param = aws_ssm.StringParameter(
            self, "ParameterB",
            parameter_name=f"/{props['namespace']}/bucket",
            string_value=bucket.bucket_name,
            description='terraform pipeline bucket'
        )

        # codebuild project meant to run in pipeline
        cb_docker_build = aws_codebuild.PipelineProject(
            self, "DockerBuild",
            project_name=f"{props['namespace']}-setup",
            build_spec=aws_codebuild.BuildSpec.from_source_filename(
                filename='terraform/cicd/pipeline_delivery/docker_build_buildspec.yml'),
            environment=aws_codebuild.BuildEnvironment(
                privileged=False,
                #build_image=aws_codebuild.LinuxBuildImage.from_ecr_repository(repository=docker_asset.repository, tag=docker_asset.asset_hash)
                build_image=aws_cdk.aws_codebuild.LinuxBuildImage.from_docker_registry(name='public.ecr.aws/f3n2w4j5/policy-as-code:latest')
            ),

            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                'tag': aws_codebuild.BuildEnvironmentVariable(
                    value='terraform')
            },
            description='Pipeline for CodeBuild',
            timeout=core.Duration.minutes(15),
        )
        scan = aws_codebuild.PipelineProject(
            self, "scan",
            project_name=f"{props['namespace']}-scan",
            build_spec=aws_codebuild.BuildSpec.from_source_filename(
                filename='scan_buildspec.yml'),
            environment=aws_codebuild.BuildEnvironment(
                privileged=False,
                #build_image=aws_codebuild.LinuxBuildImage.from_ecr_repository(repository=docker_asset.repository, tag=docker_asset.asset_hash)
                build_image=aws_cdk.aws_codebuild.LinuxBuildImage.from_docker_registry(
                    name='public.ecr.aws/f3n2w4j5/policy-as-code:latest')

            ),
            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                'tag': aws_codebuild.BuildEnvironmentVariable(
                    value='terraform')
            },
            description='Codebuild Scan',
            timeout=core.Duration.minutes(15),
        )
        # repo
        # codebuild iam permissions to read write s3
        bucket.grant_read_write(cb_docker_build)

        # codebuild permissions to interact with ecr

        core.CfnOutput(
            self, "S3Bucket",
            description="S3 Bucket",
            value=bucket.bucket_name
        )
        # cb_docker_build.role.add_managed_policy(
        #     aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
        cb_docker_build.role.add_to_policy(aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=['s3:CreateBucket'],
            resources=["*"]
            )
        )
        
        #
        # Uncomment if using terraform and regula
        #
        scan.role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess')
        )
        scan.role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('AWSKeyManagementServicePowerUser')
        )

        self.output_props = props.copy()
        self.output_props['bucket'] = bucket
        self.output_props['cb_docker_build'] = cb_docker_build
        self.output_props['cb_scan'] = scan

    # pass objects to another stack
    @property
    def outputs(self):
        return self.output_props
