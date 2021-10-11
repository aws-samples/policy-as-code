from aws_cdk import (
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    aws_codecommit,
    core,
    aws_cloudformation,
)


class Pipeline(core.Stack):
    def __init__(self, app: core.App, id: str, props, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        # define the s3 artifact
        source_output = aws_codepipeline.Artifact(artifact_name='source')
        synth = aws_codepipeline.Artifact(artifact_name='synth')
        scanned_source = aws_codepipeline.Artifact(artifact_name='scanned_source')
        # define the pipeline
        repo = aws_codecommit.Repository(self, "sourcerepo", repository_name='policy-as-code-' + self.stack_id)
        change_set_name = 'policy-as-code'
        pipeline = aws_codepipeline.Pipeline(
            self, "Pipeline",
            pipeline_name=f"{props['namespace']}",
            artifact_bucket=props['bucket'],
            stages=[
                aws_codepipeline.StageProps(
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
                        aws_codepipeline_actions.CodeCommitSourceAction(
                            repository=repo,
                            action_name='source',
                            branch='dev',
                            output=source_output,
                            trigger=aws_codepipeline_actions.CodeCommitTrigger.EVENTS


                        )
                    ]
                ),
                aws_codepipeline.StageProps(
                    stage_name='Build',
                    actions=[
                        aws_codepipeline_actions.CodeBuildAction(
                            action_name='Synth',
                            input=source_output,
                            outputs=[synth],
                            project=props['cb_docker_build'],
                            run_order=1,
                        )
                    ]
                ),
                aws_codepipeline.StageProps(
                    stage_name='ScanDeploy',
                    actions=[
                        aws_codepipeline_actions.CodeBuildAction(
                            action_name='Scan',
                            input=synth,
                            project=props['cb_scan'],
                            run_order=1,
                            outputs=[scanned_source]
                        ),
                        aws_codepipeline_actions.CloudFormationCreateReplaceChangeSetAction(
                            action_name='CreateChangeSet',
                            change_set_name=change_set_name,
                            stack_name=change_set_name,
                            # input=scanned_source,
                            template_path=aws_codepipeline.ArtifactPath(artifact=scanned_source,file_name='cdk.out/policy-as-code.template.json'),
                            run_order=2,
                            cfn_capabilities=[aws_cloudformation.CloudFormationCapabilities.NAMED_IAM],
                            admin_permissions=True
                        ),
                        aws_codepipeline_actions.CloudFormationExecuteChangeSetAction(
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
        props['bucket'].grant_read_write(pipeline.role)

        # pipeline param to get the
        pipeline_param = aws_ssm.StringParameter(
            self, "PipelineParam",
            parameter_name=f"/{props['namespace']}/pipeline",
            string_value=pipeline.pipeline_name,
            description='cdk pipeline bucket'
        )
        # cfn output
        core.CfnOutput(
            self, "PipelineOut",
            description="Pipeline",
            value=pipeline.pipeline_name
        )
