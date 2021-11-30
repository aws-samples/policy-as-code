---
title: "Fix Regula findings"
weight: 20
---

## Remediate Regula rule violations
1. Replicate the Regula run from the CodePipeline to the local environment. Run the following commands to do that:
    ```bash
    cd ~/environment/policy-as-code/terraform/app
    regula run -i custom-rules main.tf
    ```
    You should see output that looks similiar to this:
    ```
    FG_R00229: S3 buckets should have all `block public access` options enabled [High]
               https://docs.fugue.co/FG_R00229.html

      [1]: aws_s3_bucket.b
           in main.tf:25:1

    FG_S0001: S3 bucket server side encryption should be enabled using KMS (not with AWS S3-Managed Keys) [High]

      [1]: aws_s3_bucket.b
           in main.tf:25:1

    FG_R00100: S3 bucket policies should only allow requests that use HTTPS [Medium]
               https://docs.fugue.co/FG_R00100.html

      [1]: aws_s3_bucket.b
           in main.tf:25:1

    Found 3 problems.    ```
1. The first issue to remediate is blocking public access to the S3 bucket.
    ```
    FG_R00229: S3 buckets should have all `block public access` options enabled [High]
               https://docs.fugue.co/FG_R00229.html

      [1]: aws_s3_bucket.b
           in main.tf:25:1    
    ```
    To address this add the following to terraform file **policy-as-code/terraform/app/main.tf** where it says insert to enable block public access:
    ```bash
    resource "aws_s3_bucket_public_access_block" "c" {
      bucket = "${aws_s3_bucket.b.id}"
      block_public_acls = true
      block_public_policy = true
      ignore_public_acls = true
      restrict_public_buckets = true
    }
    ```
    Below shows the resource **aws_s3_bucket_public_access_block** added to **policy-as-code/terraform/app/main.tf**. Once inserted it should look like this:
    ```
    // Insert code to block S3 bucket public access below
    resource "aws_s3_bucket_public_access_block" "c" {
      bucket = "${aws_s3_bucket.b.id}"
      block_public_acls = true
      block_public_policy = true
      ignore_public_acls = true
      restrict_public_buckets = true
    }
    // End of block S3 bucket public access
    ```
1. Run regula again:
    ```bash
    cd ~/environment/policy-as-code/terraform/app
    regula run -i custom-rules main.tf
    ```
    The output will look something like this:
    ```
    FG_S0001: S3 bucket server side encryption should be enabled using KMS (not with AWS S3-Managed Keys) [High]

        [1]: aws_s3_bucket.b
            in main.tf:25:1

    FG_R00100: S3 bucket policies should only allow requests that use HTTPS [Medium]
               https://docs.fugue.co/FG_R00100.html

        [1]: aws_s3_bucket.b
            in main.tf:25:1

    Found 2 problems.
    ```
1. Server side encryption needs to be enabled and the KMS key resource needs to be added. Copy the code snippet below and insert below the commented section **// Insert KMS key here** to the file **policy-as-code/terraform/app/main.tf**:
    ```bash
    resource "aws_kms_key" "a" {
      description = "S3 KMS key"
      deletion_window_in_days = 7
    }
    ```
    Comment out or remove the property **sse_algorithm = AES256** as we want to use the AWS managed key. Uncomment the properties **sse_algorithm** and **kms_master_key_id** in the S3 bucket resource under the comment **// Uncomment to use KMS key**. It should look something like this after your done:
    ```
    ...
    // Uncomment to use KMS key
    sse_algorithm     = "aws:kms"
    kms_master_key_id = aws_kms_key.a.key_id
    ...
    ```
    Save the file **policy-as-code/terraform/app/main.tf** and run:
    ```bash
    cd ~/environment/policy-as-code/terraform/app
    regula run -i custom-rules main.tf    
    ```
1. Regula has uncovered an issue with our KMS key resource. The output should look like this:
    ```
    FG_R00036: KMS CMK rotation should be enabled [Medium]
               https://docs.fugue.co/FG_R00036.html

      [1]: aws_kms_key.a
           in main.tf:18:1
           KMS key rotation should be enabled

    FG_R00100: S3 bucket policies should only allow requests that use HTTPS [Medium]
               https://docs.fugue.co/FG_R00100.html

      [1]: aws_s3_bucket.b
           in main.tf:26:1

    Found 2 problems.
    ```
    This can be easily fixed by enabling key rotation. Add the line below into our kms key resource.
    ```bash
    enable_key_rotation = true
    ```
    The KMS key resource should look like below:
    ```
    // Insert KMS key here
    resource "aws_kms_key" "a" {
      description = "S3 KMS key"
      deletion_window_in_days = 7
      enable_key_rotation = true
    }
    // KMS key
    ```
1. The final finding to address is adding a S3 bucket policy that will only allow requests that use HTTPS. Add the following code snippet to the file **policy-as-code/terraform/app/main.tf** below the comment **// Insert S3 bucket policy here**:
    ```bash
    resource "aws_s3_bucket_policy" "d" {
      bucket = "${aws_s3_bucket.b.id}"
      policy = jsonencode({
        Id = "TLS-SSL-Policy"
        Version = "2012-10-17"
        Statement = [
          {
            Sid = "AllowSSLRequestsOnly"
            Action = "s3:*"
            Effect = "Deny"
            Resource = [
              "${aws_s3_bucket.b.id}"
            ]
            Condition = {
              Bool = {
                "aws:SecureTransport" = "false"
              }
            }
            Principal = "*"
          }
        ]
      })
    }
    ```
    The file **policy-as-code/terraform/app/main.tf** should look like:
    ```
    ...
    // Insert S3 bucket policy here
    resource "aws_s3_bucket_policy" "d" {
      bucket = "${aws_s3_bucket.b.id}"
      policy = jsonencode({
        Id = "TLS-SSL-Policy"
        Version = "2012-10-17"
        Statement = [
          {
            Sid = "AllowSSLRequestsOnly"
            Action = "s3:*"
            Effect = "Deny"
            Resource = [
              "${aws_s3_bucket.b.arn}"
            ]
            Condition = {
              Bool = {
                "aws:SecureTransport" = "false"
              }
            }
            Principal = "*"
          }
        ]
      })
    }
    // End of S3 bucket policy
    ...
    ```
1. Commit the changes to the repo and push to the source CodeCommit repo to kick of the pipeline.
    ```bash
    cd ~/environment/policy-as-code/
    git commit -a -m "fix regula violations in s3_deployment.py"
    git push
    ```

