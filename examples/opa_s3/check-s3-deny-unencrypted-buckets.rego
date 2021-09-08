package s3.bucket_encryption

resource_type = "AWS::S3::Bucket"

# Only Allow 'aws:kms' which is SSE-KMS (AWS KMS-Managed key), 'AES256' is S3-SSE, AWS S3-Managed Key and not allowed.
# SSE-KMS supports AWS Managed CMKs or Customer Managed CMKs.
allowed_sse_algorithms = {
  "aws:kms"
}

default allow = true

allow = false {
    count(violation) > 0
}

violation[retVal] {
    count(deny_sse_algorithm) > 0
    retVal := { ms.template |
        s3 = deny_sse_algorithm[_]
        ms.template := {
            "resource": s3,
            "decision": "deny",
            "message": "S3 bucket server side encryption (SSE) is required. Objects can be encrypted **only** with KMS-Managed Keys (SSE-KMS)."
        }
    }
}

violation[retVal] {
    count(deny_without_sse) > 0
    retVal := { ms.template |
        s3 = deny_without_sse[_]
        ms.template := {
            "resource": s3,
            "decision": "deny",
            "message": "S3 bucket server side encryption (SSE) is required. Please enable BucketEncryption to protect data-at-rest."
        }
    }
}

deny_sse_algorithm[resource] {
    some resource
    input.Resources[resource].Type == resource_type
    algorithms := { algorithm |
        algorithm := input.Resources[resource].Properties.BucketEncryption.ServerSideEncryptionConfiguration[_].ServerSideEncryptionByDefault.SSEAlgorithm
    }
    #trace(sprintf("Resource=%v, algorithms=%v, allowed_sse_algorithms=%v", [resource,algorithms, allowed_sse_algorithms]))
    count(algorithms) > 0
    count(algorithms - allowed_sse_algorithms) > 0
}

deny_without_sse[resource] {
    some resource
    input.Resources[resource].Type == resource_type
    not input.Resources[resource].Properties.BucketEncryption
}
