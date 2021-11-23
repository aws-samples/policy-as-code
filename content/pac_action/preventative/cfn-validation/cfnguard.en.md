---
title: "Fix cfn-guard findings"
weight: 40
---

## Remediate cfn-guard rule violations
1. As from before replicate cfn-guard run in the local environment. Run the following commands to do that:
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code/cdk/app;cdk synth;cfn-guard validate -r rules/cfn-guard -d cdk.out/policy-as-code.template.json --show-summary all
    :::

    Below is what cfn-guard should output, this will look similiar to what is in the CodeBuild logs:
    ```
    cdk.out/policy-as-code.template.json Status = SKIP
    SKIP rules
    kms/kms.guard/deny_kms_key_being_used_outside_account    SKIP
    kms/kms.guard/deny_kms_key_without_key_rotation          SKIP
    ---
    cdk.out/policy-as-code.template.json Status = FAIL
    SKIP rules
    s3/bucket_policies.guard/deny_s3_buckets_over_insecure_transport            SKIP
    s3/bucket_policies.guard/check_s3_buckets_have_deny_for_unencrypted_puts    SKIP
    FAILED rules
    s3/bucket_policies.guard/check_all_s3_buckets_have_policy                   FAIL
    ---
    `- File(, Status=FAIL)[Context=File(rules=3)]
    |- Rule(check_all_s3_buckets_have_policy, Status=FAIL)[Context=check_all_s3_buckets_have_policy]
    |  `- Check was not compliant as variable in context [ %s3_policy_bucket_refs not EMPTY  ] was not empty. Message [Bucket policies must be defined within the same stack template]
    cdk.out/policy-as-code.template.json Status = PASS
    PASS rules
    s3/bucket_public_exposure.guard/deny_s3_access_control           PASS
    s3/bucket_public_exposure.guard/deny_s3_notification_settings    PASS
    s3/bucket_public_exposure.guard/deny_s3_cors_settings            PASS
    s3/bucket_public_exposure.guard/deny_s3_website_configuration    PASS
    s3/bucket_public_exposure.guard/deny_s3_public_access            PASS
    ---
    cdk.out/policy-as-code.template.json Status = FAIL
    SKIP rules
    s3/bucket_server_side_encryption.guard/check_s3_sse_kms_local_stack_only    SKIP
    PASS rules
    s3/bucket_server_side_encryption.guard/check_s3_sse_is_enabled              PASS
    FAILED rules
    s3/bucket_server_side_encryption.guard/check_s3_sse_kms_only                FAIL
    ---
    `- File(, Status=FAIL)[Context=File(rules=3)]
    |- Rule(check_s3_sse_kms_only, Status=FAIL)[Context=check_s3_sse_kms_only]
    |  `- Rule(check_s3_sse_kms, Status=FAIL)[Context=check_s3_sse_kms]
    |     `- Check was not compliant as property value [Path=/Resources/Bucket83908E77/Properties/BucketEncryption/ServerSideEncryptionConfiguration/0/ServerSideEncryptionByDefault/SSEAlgorithm, Value="AES256"] not equal to value [Path=, Value="aws:kms"]. Message = [Algorithm must be set of 'aws:kms']
    |     `- Check was not compliant as property [KMSMasterKeyID] is missing. Value traversed to [Path=/Resources/Bucket83908E77/Properties/BucketEncryption/ServerSideEncryptionConfiguration/0/ServerSideEncryptionByDefault, Value={"SSEAlgorithm":"AES256"}]. Message = [KMS Key must be set]
    ```
1. The first issue that fails is:
    ```
    s3/bucket_policies.guard/check_all_s3_buckets_have_policy                   FAIL
    ```
    Examine the file **./policy-as-code/cdk/app/cdk.out/policy-as-code.template.json**. There is no resource AWS::S3::BucketPolicy defined.

    As from before modifying the CDK source code will generate the CFN template. Setting to **true**
    the [**enforceSSL**](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html#enforcessl) in **Construct Properties** will force the creation of a S3 bucket policy that
    will require TLS/SSL. As a side effect this will also comply with the rule:
    ```
    s3/bucket_policies.guard/deny_s3_buckets_over_insecure_transport            SKIP
    ```
    Which is currently being skipped because there is no bucket policy to check.
    Open the file **./policy-as-code/cdk/app/s3_deployment.py** and find the commented out section:
    ```
    ...
        # Uncomment to enforce_ssl
        # enforce_ssl=True,
    ...
    ```
    Uncomment the line **enforce_ssl=True,** It should look like this after modified:
    ```
    ...
        # Uncomment to enforce_ssl
        enforce_ssl=True,    
    ...
    ```
    Save the file using Cloud9 menu File->Save
1. Validate the code by running:
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code/cdk/app;cdk synth;cdk synth;cfn-guard validate -r rules/cfn-guard -d cdk.out/policy-as-code.template.json --show-summary all
    :::
    Although the s3 bucket policies:
    ```
    PASS rules
    s3/bucket_policies.guard/check_all_s3_buckets_have_policy                   PASS
    s3/bucket_policies.guard/deny_s3_buckets_over_insecure_transport            PASS
    ```
    Are passing. The s3 bucket policy:
    ```
    FAILED rules
    s3/bucket_policies.guard/check_s3_buckets_have_deny_for_unencrypted_puts    FAIL
    ```
    The rule that is failing is **check_s3_buckets_have_deny_for_unencrypted_puts** but what seems to be
    causing it to fail is the rule that it calls **check_unencrypted_deny_statement**
    ```
    ...
   - Rule(check_s3_buckets_have_deny_for_unencrypted_puts, Status=FAIL)[Context=check_s3_buckets_have_deny_for_unencrypted_puts]
      `- Disjunction(Status = FAIL)[Context=cfn_guard::rules::exprs::GuardClause#disjunction]
         |- Rule(check_unencrypted_deny_statement, Status=FAIL)[Context=check_unencrypted_deny_statement]
         |  `- Disjunction(Status = FAIL)[Context=cfn_guard::rules::exprs::RuleClause#disjunction]
         |     |- Rule(check_sse, Status=FAIL)[Context=check_sse]
         |     |  `- Disjunction(Status = FAIL)[Context=cfn_guard::rules::exprs::RuleClause#disjunction]
         |     |     `- Check was not compliant as property [StringNotEqualsIfExists.%key] to compare from is missing. Value traversed to [Path=/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition, Value={"Bool":{"aws:SecureTransport":"false"}}].
         |     |     `- Rule(check_null_string_not_eq_combo, Status=FAIL)[Context=check_null_string_not_eq_combo]
         |     |        `- Check was not compliant as property [StringNotEquals.%key] to compare from is missing. Value traversed to [Path=/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition, Value={"Bool":{"aws:SecureTransport":"false"}}]. Message = [ DENY statement does not contain any StringNotEquals Condition to match value ]
         |     |        `- Check was not compliant as property [/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition/Bool] was not empty. Message = [ DENY statement must contain only one StringNotEquals key ]
         |     |        `- Check was not compliant as property [Null.%key] to compare from is missing. Value traversed to [Path=/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition, Value={"Bool":{"aws:SecureTransport":"false"}}]. Message = [ DENY statement does not contain any Null checks == true ]
         |     |        `- Check was not compliant as property [/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition/Bool] was not empty. Message = [ DENY statement mut contain only one Null key ]
         |     |- Rule(check_sse, Status=FAIL)[Context=check_sse]
         |     |  `- Disjunction(Status = FAIL)[Context=cfn_guard::rules::exprs::RuleClause#disjunction]
         |     |     `- Check was not compliant as property [StringNotEqualsIfExists.%key] to compare from is missing. Value traversed to [Path=/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition, Value={"Bool":{"aws:SecureTransport":"false"}}].
         |     |     `- Rule(check_null_string_not_eq_combo, Status=FAIL)[Context=check_null_string_not_eq_combo]
         |     |        `- Check was not compliant as property [StringNotEquals.%key] to compare from is missing. Value traversed to [Path=/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition, Value={"Bool":{"aws:SecureTransport":"false"}}]. Message = [ DENY statement does not contain any StringNotEquals Condition to match value ]
         |     |        `- Check was not compliant as property [/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition/Bool] was not empty. Message = [ DENY statement must contain only one StringNotEquals key ]
         |     |        `- Check was not compliant as property [Null.%key] to compare from is missing. Value traversed to [Path=/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition, Value={"Bool":{"aws:SecureTransport":"false"}}]. Message = [ DENY statement does not contain any Null checks == true ]
         |     |        `- Check was not compliant as property [/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition/Bool] was not empty. Message = [ DENY statement mut contain only one Null key ]
         |     `- Rule(check_kms_id, Status=FAIL)[Context=check_kms_id]
         |        `- Disjunction(Status = FAIL)[Context=cfn_guard::rules::exprs::RuleClause#disjunction]
         |           `- Check was not compliant as property [StringNotEqualsIfExists.%key] is missing. Value traversed to [Path=/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition, Value={"Bool":{"aws:SecureTransport":"false"}}].
         |           `- Rule(check_null_string_not_eq_combo, Status=FAIL)[Context=check_null_string_not_eq_combo]
         |              `- Check was not compliant as property [StringNotEquals.%key] to compare from is missing. Value traversed to [Path=/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition, Value={"Bool":{"aws:SecureTransport":"false"}}]. Message = [ DENY statement does not contain any StringNotEquals Condition to match value ]
         |              `- Check was not compliant as property [/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition/Bool] was not empty. Message = [ DENY statement must contain only one StringNotEquals key ]
         |              `- Check was not compliant as property [Null.%key] to compare from is missing. Value traversed to [Path=/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition, Value={"Bool":{"aws:SecureTransport":"false"}}]. Message = [ DENY statement does not contain any Null checks == true ]
         |              `- Check was not compliant as property [/Resources/BucketPolicyE9A3008A/Properties/PolicyDocument/Statement/0/Condition/Bool] was not empty. Message = [ DENY statement mut contain only one Null key ]
    ...
    ```
    Inspect the rules file by opening **./policy-as-code/cdk/app/rules/cfn-guard/s3/bucket_policies.guard**. Find the rule **check_unencrypted_deny_statement** and examine the clauses:
    ```
    rule check_unencrypted_deny_statement(statements) {
    #
    # Select all DENY statements in the policy and check for Action == 's3:PutObject'
    # and Principal == '*'
    #
    let deny_statements = %statements[ Effect == 'Deny' ]

    %deny_statements not empty
        << There are no DENY statements in the policy document >>

    # Disabled this rule, don't really understand why it is a failure to just deny s3:PutObject
    # CDK will generate a bucket policy that has s3:*
    #some %deny_statements {
    #    Action == 's3:PutObject'
    #        << DENY MUST contain only s3:PutObject action and nothing else >>

    some %deny_statements {
        Principal == '*' or
        Principal.AWS == '*'
            << Principal MUST be '*' or {AWS: '*'} for DENY, To keep policy simple do not include others >>
    }


    check_sse(%deny_statements, 's3:x-amz-server-side-encryption', 'AES256', %name)     or
    check_sse(%deny_statements, 's3:x-amz-server-side-encryption', 'aws:kms', %name)    or
    check_kms_id(%deny_statements, 's3:x-amz-server-side-encryption-aws-kms-key-id', %name)

    }
    ```
    The statement check_sse and check_kms_id are failing.
    To better understand this checkout this AWS doc [Protecting data using server-side encryption with Amazon S3-managed encryption keys (SSE-S3)](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingServerSideEncryption.html). It specifies a bucket policy that needs to be added to the current
    bucket policy. Examine the CFN template that was generated, open file **./policy-as-code/cdk/app/cdk.out/policy-as-code.template.json**. It has the following bucket policy:
    ```
    "BucketPolicyE9A3008A": {
      "Type": "AWS::S3::BucketPolicy",
      "Properties": {
        "Bucket": {
          "Ref": "Bucket83908E77"
        },
        "PolicyDocument": {
          "Statement": [
            {
              "Action": "s3:*",
              "Condition": {
                "Bool": {
                  "aws:SecureTransport": "false"
                }
              },
              "Effect": "Deny",
              "Principal": {
                "AWS": "*"
              },
              "Resource": [
                {
                  "Fn::GetAtt": [
                    "Bucket83908E77",
                    "Arn"
                  ]
                },
                {
                  "Fn::Join": [
                    "",
                    [
                      {
                        "Fn::GetAtt": [
                          "Bucket83908E77",
                          "Arn"
                        ]
                      },
                      "/*"
                    ]
                  ]
                }
              ]
            }
          ],
          "Version": "2012-10-17"
        }
      },
      "Metadata": {
        "aws:cdk:path": "policy-as-code/Bucket/Policy/Resource"
      }
    },
    ```

    Focusing on the messages:
    ```
    Message = [ DENY statementmust contain only one StringNotEquals key ]
    Message = [ DENY statement does notcontain any Null checks == true ]
    Message = [ DENY statementmut contain only one Null key ]
    ```
    The cfn-guard messages indicate the current CFN template is missing deny statements in the S3 bucket policy. Address this by adding the deny statements to the S3 bucket policy. 
1.  Add the deny statements by updating the CDK source code, open the file **./policy-as-code/cdk/app/s3_deployment.py**. Find the section of the file with the comment:
    ```
        ...
        # Insert new policy statement that denies s3:PutObject if encryption header is not set
        # End of new policy statement
        ...
    ```
    Insert the following block of code:
    :::code{showCopyAction=true}
        unencrypted_put_conditions = [
            {'StringNotEquals': { 's3:x-amz-server-side-encryption': 'AES256'}},
            {'StringNotEquals': { 's3:x-amz-server-side-encryption': 'aws:kms'}},
            {'Null': {'s3:x-amz-server-side-encryption': True}}
        ]
        
        for condition in unencrypted_put_conditions:
            bucket.add_to_resource_policy(
                aws_iam.PolicyStatement(
                    actions=[
                        "s3:PutObject"
                    ],
                    effect=aws_iam.Effect.DENY,
                    principals=[
                        aws_iam.AnyPrincipal()
                    ],
                    resources=[
                        bucket.bucket_arn + "/*"
                    ],
                    conditions=condition
                )
            )
    :::
    When inserted it should look like this:
    ```
        ...
        # Insert new policy statement that denies s3:PutObject if encryption header is not set
        unencrypted_put_conditions = [
            {'StringNotEquals': { 's3:x-amz-server-side-encryption': 'AES256'}},
            {'StringNotEquals': { 's3:x-amz-server-side-encryption': 'aws:kms'}},
            {'Null': {'s3:x-amz-server-side-encryption': True}}
        ]
        
        for condition in unencrypted_put_conditions:
            bucket.add_to_resource_policy(
                aws_iam.PolicyStatement(
                    actions=[
                        "s3:PutObject"
                    ],
                    effect=aws_iam.Effect.DENY,
                    principals=[
                        aws_iam.AnyPrincipal()
                    ],
                    resources=[
                        bucket.bucket_arn + "/*"
                    ],
                    conditions=condition
                )
            )
        # End of new policy statement
        ...
    ```
    Save this file in Cloud9 with the menu File->Save.
1. Validate the code by running:
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code/cdk/app;cdk synth;cdk synth;cfn-guard validate -r rules/cfn-guard -d cdk.out/policy-as-code.template.json --show-summary all
    :::
    The output after cfn-guard runs should look like this:
    ```
    cdk.out/policy-as-code.template.json Status = SKIP
    SKIP rules
    kms/kms.guard/deny_kms_key_being_used_outside_account    SKIP
    kms/kms.guard/deny_kms_key_without_key_rotation          SKIP
    ---
    cdk.out/policy-as-code.template.json Status = PASS
    PASS rules
    s3/bucket_policies.guard/check_all_s3_buckets_have_policy                   PASS
    s3/bucket_policies.guard/deny_s3_buckets_over_insecure_transport            PASS
    s3/bucket_policies.guard/check_s3_buckets_have_deny_for_unencrypted_puts    PASS
    ---
    cdk.out/policy-as-code.template.json Status = PASS
    PASS rules
    s3/bucket_public_exposure.guard/deny_s3_access_control           PASS
    s3/bucket_public_exposure.guard/deny_s3_notification_settings    PASS
    s3/bucket_public_exposure.guard/deny_s3_cors_settings            PASS
    s3/bucket_public_exposure.guard/deny_s3_website_configuration    PASS
    s3/bucket_public_exposure.guard/deny_s3_public_access            PASS
    ---
    cdk.out/policy-as-code.template.json Status = FAIL
    SKIP rules
    s3/bucket_server_side_encryption.guard/check_s3_sse_kms_local_stack_only    SKIP
    PASS rules
    s3/bucket_server_side_encryption.guard/check_s3_sse_is_enabled              PASS
    FAILED rules
    s3/bucket_server_side_encryption.guard/check_s3_sse_kms_only                FAIL
    ---
    `- File(, Status=FAIL)[Context=File(rules=3)]
       |- Rule(check_s3_sse_kms_only, Status=FAIL)[Context=check_s3_sse_kms_only]
       |  `- Rule(check_s3_sse_kms, Status=FAIL)[Context=check_s3_sse_kms]
       |     `- Check was not compliant as property value [Path=/Resources/Bucket83908E77/Properties/   BucketEncryption/ServerSideEncryptionConfiguration/0/ServerSideEncryptionByDefault/SSEAlgorithm,   Value="AES256"] not equal to value [Path=, Value="aws:kms"]. Message = [Algorithm must be set of  'aws:kms']
       |     `- Check was not compliant as property [KMSMasterKeyID] is missing. Value traversed to [Path=/ Resources/Bucket83908E77/Properties/BucketEncryption/ServerSideEncryptionConfiguration/0/    ServerSideEncryptionByDefault, Value={"SSEAlgorithm":"AES256"}]. Message = [KMS Key must be set]
    ```
    The rule **s3/bucket_server_side_encryption.guard/check_s3_sse_kms_only** is not satisfied because it expects the S3 property **BucketEncryption** property to use AWS KMS-managed keys(SSE-KMS). Examine the CFN template to see what is currently configured for **BucketEncryption**, open the file **./policy-as-code/cdk/app/cdk.out/policy-as-code.template.json** the following is what is currently configured:
    ```
        ...
        "BucketEncryption": {
          "ServerSideEncryptionConfiguration": [
            {
              "ServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
              }
            }
          ]
        },
        ...
    ```
    In order to comply with this rule the **BucketEncryption** should look something like:
    ```
        ...
        "BucketEncryption": {
            "ServerSideEncryptionConfiguration": [
                {
                    "ServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms",
                        "KMSMasterKeyID": "KMS-KEY-ARN"
                    }
                }
            ]
        }
        ...
    ```
    This will require creating a KMS key as well is configuring the S3 bucket to use the KMS key.
1. Creating the KMS key and configuring the S3 bucket to use the KMS key will require modification to the CDK source code. Open the file **./policy-as-code/cdk/app/s3_deployment.py** and find the following section:
    ```
        ...
        # Insert KMS key here

        # End of KMS key here
        ...
    ```
    Copy the following code snippet. It creates the KMS key for the S3 bucket:
    :::code{showCopyAction=true showLineNumbers=false}
        kms_key = aws_kms.Key(self, 'KmsKey',
            enable_key_rotation=True
        )
        
        kms_key.add_to_resource_policy(
            aws_iam.PolicyStatement(
                actions=[
                    '*',
                    'kms:*'
                ],
                effect=aws_iam.Effect.DENY,
                principals=[
                        aws_iam.AnyPrincipal()
                ],
                resources=[
                        "*"
                ],
                conditions={'StringNotEquals': {'kms:CallerAccount': self.account}}
            )
        )
    :::
    The result should look like this:
    ```
        ...
        # Insert KMS key here
        kms_key = aws_kms.Key(self, 'KmsKey',
            enable_key_rotation=True
        )
        
        kms_key.add_to_resource_policy(
            aws_iam.PolicyStatement(
                actions=[
                    '*',
                    'kms:*'
                ],
                effect=aws_iam.Effect.DENY,
                principals=[
                        aws_iam.AnyPrincipal()
                ],
                resources=[
                        "*"
                ],
                conditions={'StringNotEquals': {'kms:CallerAccount': self.account}}
            )
        )
        # End of KMS key here
        ...
    ```
    Uncomment the line **buket_key_enabled=True,**:
    ```
        ...
        # Uncomment bucket_key_enabled=True, once the KMS key is defined
        # bucket_key_enabled=True,
        ...
    ```
    This should look like this after completed:
    ```
        ...
        # Uncomment bucket_key_enabled=True, once the KMS key is defined
        bucket_key_enabled=True,
        ...
    ```
    Finally remove the line **encryption=aws_s3.BucketEncryption.S3_MANAGED,** and uncomment **encryption=aws_s3.BucketEncryption.KMS,**:
    ```
        ...
        # Once you define the KMS key uncomment encryption=aws_s3.BucketEncryption.KMS attribute
        # Remove the encryption=aws_s3.BucketEncryption.S3_MANAGED completely
        # encryption=aws_s3.BucketEncryption.KMS,
            
        # Uncommment to make checkov pass
        encryption=aws_s3.BucketEncryption.S3_MANAGED,
        ...
    ```
    When finished it should look like this:
    ```
        ...
        # Once you define the KMS key uncomment encryption=aws_s3.BucketEncryption.KMS attribute
        # Remove the encryption=aws_s3.BucketEncryption.S3_MANAGED completely
        encryption=aws_s3.BucketEncryption.KMS,
            
        # Uncommment to make checkov pass
        ...
    ```
    These changes to S3 bucket with in CDK is needed to configure the S3 with the KMS key that will be created. Save the file in Cloud9 under menu File->Save.
1. Validate the code by running:
    :::code{showCopyAction=true showLineNumbers=false}
    cd ~/environment/policy-as-code/cdk/app;cdk synth;cdk synth;cfn-guard validate -r rules/cfn-guard -d cdk.out/policy-as-code.template.json --show-summary all
    :::
    The output after cfn-guard runs should look like this:
    ```
    cdk.out/policy-as-code.template.json Status = PASS
    PASS rules
    kms/kms.guard/deny_kms_key_being_used_outside_account    PASS
    kms/kms.guard/deny_kms_key_without_key_rotation          PASS
    ---
    cdk.out/policy-as-code.template.json Status = PASS
    PASS rules
    s3/bucket_policies.guard/check_all_s3_buckets_have_policy                   PASS
    s3/bucket_policies.guard/deny_s3_buckets_over_insecure_transport            PASS
    s3/bucket_policies.guard/check_s3_buckets_have_deny_for_unencrypted_puts    PASS
    ---
    cdk.out/policy-as-code.template.json Status = PASS
    PASS rules
    s3/bucket_public_exposure.guard/deny_s3_access_control           PASS
    s3/bucket_public_exposure.guard/deny_s3_notification_settings    PASS
    s3/bucket_public_exposure.guard/deny_s3_cors_settings            PASS
    s3/bucket_public_exposure.guard/deny_s3_website_configuration    PASS
    s3/bucket_public_exposure.guard/deny_s3_public_access            PASS
    ---
    cdk.out/policy-as-code.template.json Status = PASS
    PASS rules
    s3/bucket_server_side_encryption.guard/check_s3_sse_is_enabled              PASS
    s3/bucket_server_side_encryption.guard/check_s3_sse_kms_only                PASS
    s3/bucket_server_side_encryption.guard/check_s3_sse_kms_local_stack_only    PASS
    ```
    Congratulations! At this point the AWS CodePipeline should be able to deploy the S3 CDK application with no issues. Run the following command:
    :::code{showCopyAction=true showLineNumbers=false}
    git commit -a -m "fixed issues with S3 CDK and now complies with cfn-guard rules";git push
    :::
1. View the CodePipeline in your account. Instructions to do that is [here](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-view-console.html#pipelines-list-console.). Give it about a minute to restart. Verify that the cfn-guard rules have passed. At this point the pipeline should deploy the S3 CDK application.
1. Validate that the S3 bucket exists after the AWS CodePipeline completes. In the AWS Console browse over to S3. Look for a bucket with the prefix 'Bucket'.

