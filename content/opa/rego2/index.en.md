---
title: "S3 Bucket Example"
weight: 44
---

Let's explore an example using S3 bucket as our resource.

### Deny unencrypted buckets 

Create the file **template.json** with the contents below:

```
{
  "Resources": {
    "EncryptedS3Bucket": {
      "Type": "AWS::S3::Bucket",
      "Properties": {
        "BucketName": "encryptedbucket-test",
        "BucketEncryption": {
          "ServerSideEncryptionConfiguration": [
            {
              "ServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms",
                "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789:key/056ea50b-1013-3907-8617-c93e474e400"
              },
              "BucketKeyEnabled": true
            }
          ]
        }
      },
      "Metadata": {
        "aws:cdk:path": "foo/Counter/S3/Resource"
      }
    },
    "InvalidEncryptedS3Bucket": {
      "Type": "AWS::S3::Bucket",
      "Properties": {
        "BucketName": "invalid-encryptedbucket-test",
        "BucketEncryption": {
          "ServerSideEncryptionConfiguration": [
            {
              "ServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
              }
            }
          ]
        }
      },
      "Metadata": {
        "aws:cdk:path": "foo/Counter/S3/Resource"
      }
    },
    "Invalid2EncryptedS3Bucket": {
      "Type": "AWS::S3::Bucket",
      "Properties": {
        "BucketName": "invalid2-encryptedbucket-test",
      },
      "Metadata": {
        "aws:cdk:path": "foo/Counter/S3/Resource"
      }
    }
  }
}
```
We would like to enforce encryption on buckets with the use of a CMK and not use of the default S3 bucket encryption key.
{{% notice note %}}
This template contains three buckets, first bucket is valid. second bucket is invalid - due to the algorithm, third bucket is invalid - does not enable encryption
{{% /notice %}}




Create a new file **check-s3-deny-unencrypted-buckets.rego** with the contents below:
```
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
    retVal := { msgJson |
        s3 = deny_sse_algorithm[_]
        msgJson := {
            "resource": s3,
            "decision": "deny",
            "message": "S3 bucket server side encryption (SSE) is required. Objects can be encrypted **only** with KMS-Managed Keys (SSE-KMS)."
        }
    }
}

violation[retVal] {
    count(deny_without_sse) > 0
    retVal := { msgJson |
        s3 = deny_without_sse[_]
        msgJson := {
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

```
#### Explanation
This rule is different from the previous examples. In this case we have 2 "violation" rules. Rego will evaluate both rules as a logical OR.

By default every line we write in a rule is a logical AND operator. If one of the lines fail, the rule fails. Partial rules allow us to implement a logical OR.

In this case, a violation occurs if either the bucket encryption does not exist or if the encryption algorithm used is not allowed. Let's run the rule and look at the results
```
opa eval -i template.json -d check-s3-deny-unencrypted-buckets.rego data.s3.bucket_encryption
```
Results:
```
{
  "result": [
    {
      "expressions": [
        {
          "value": {
            "allow": false,
            "allowed_sse_algorithms": [
              "aws:kms"
            ],
            "deny_sse_algorithm": [
              "InvalidEncryptedS3Bucket"
            ],
            "deny_without_sse": [
              "Invalid2EncryptedS3Bucket"
            ],
            "resource_type": "AWS::S3::Bucket",
            "violation": [
              [
                {
                  "decision": "deny",
                  "message": "S3 bucket server side encryption (SSE) is required. Objects can be encrypted **only** with KMS-Managed Keys (SSE-KMS).",
                  "resource": "InvalidEncryptedS3Bucket"
                }
              ],
              [
                {
                  "decision": "deny",
                  "message": "S3 bucket server side encryption (SSE) is required. Please enable BucketEncryption at the object level to protect data-at-rest.",
                  "resource": "Invalid2EncryptedS3Bucket"
                }
              ]
            ]
          },
          "text": "data.s3.bucket_encryption",
          "location": {
            "row": 1,
            "col": 1
          }
        }
      ]
    }
  ]
```
You can see the rule did not pass; allow is false. You can also see the violation array with two instances of buckets that did not comply. A corresponding message is also provided.

Can you fix the buckets, so the rule will pass?

#### Comprehension
In the deny_sse_algorithm you may notice the statement is different from others we have looked at. This type of statement is called a comprehension. This tells Rego we are going to run a query which includes a result.

Let's look how to build Comprehension expression:
```
algorithms := { algorithm |
  algorithm := input.Resources[resource].Properties.BucketEncryption.ServerSideEncryptionConfiguration[_].ServerSideEncryptionByDefault.SSEAlgorithm
  }
```
The external variable **algorithms** will hold the result of the query which is usually a set. The query content exist in the curly braces.

We declare the local variable **algorithm** and then assign a statement to this variable. This should look familiar because queries are just like any other rule in Rego only the scope of evaluating them is changed.

You can read more about [Comprehension](https://www.openpolicyagent.org/docs/latest/policy-language/#comprehensions)

{{% notice tip %}}
You can write nested Comprehension expressions
{{% /notice %}}
