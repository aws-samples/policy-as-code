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
  region  = "us-east-1"
}

// Insert KMS key here
// KMS key


resource "aws_s3_bucket" "b" {
  bucket_prefix = "terraform-regula-validation"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
        // Uncomment to use KMS key
        // sse_algorithm     = "aws:kms"
        // kms_master_key_id = aws_kms_key.a.key_id
      }
      bucket_key_enabled = true
    }
  }
}

// Insert code to block S3 bucket public access below
// End of block S3 bucket public access

// Insert S3 bucket policy here
// End of S3 bucket policy
