terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "us-east-2"
}

/*
resource "aws_kms_key" "a" {
  description = "S3 KMS key"
  deletion_window_in_days = 10
  enable_key_rotation = true
}
*/

resource "aws_s3_bucket" "b" {
  bucket_prefix = "terraform-regula-validation"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
        # sse_algorithm     = "aws:kms"
        # kms_master_key_id = aws_kms_key.a.key_id
      }
      # bucket_key_enabled = true
    }
  }
}

/*
resource "aws_s3_bucket_public_access_block" "c" {
  bucket = "${aws_s3_bucket.b.id}"
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

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

*/
