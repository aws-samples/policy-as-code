---
title: "AWS Costs"
weight: 200
---
This workshop will take approximately 2 hours to complete. It uses the following AWS services:
- [AWS Cloud9 Pricing](https://aws.amazon.com/cloud9/pricing/)
    - [AWS Cloud9 Pricing](https://aws.amazon.com/ec2/pricing/on-demand/)- t3.large - 2 hours $0.17
    - [AWS Elastic Block Storage Pricing](https://aws.amazon.com/ebs/pricing/) - 100GB - 2 hours 0.03
- [AWS CodeBuild Pricing](https://aws.amazon.com/codebuild/pricing/) - general1.small - 2 hours 0.00 (Free Tier Pricing)
- [AWS CodePipeline Pricing](https://aws.amazon.com/codepipeline/pricing/) - 1 active pipeline - 2 hours 0.00 (Free Tier Pricing)
- [Amazon S3 Pricing](https://aws.amazon.com/s3/pricing/) - 1 bucket 0 bytes - 2 hours 0.00
- [AWS CodeCommit Pricing](https://aws.amazon.com/codecommit/pricing/) - 1 user, 1 repo - 2 hours 0.00 (Free Tier Pricing)
- [AWS Config Pricing](https://aws.amazon.com/config/pricing/) - 100 rule evaluations - 0.01

Total: $0.24 for 2 hours

If you are using Cloud9 and forget to delete the instance, your instance should shutdown in 30 minutes (assuming there is no activity). If you forget to cleanup your monthly cost will be approximately $10.33 due to a the gp2 EBS volume. Click here to view [cleanup instructions](/cleanup)
