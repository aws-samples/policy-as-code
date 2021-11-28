# Policy as Code

## Overview
This repo contains the source for both the content and examples for the [Policy as Code Workshop](https://catalog.us-east-1.prod.workshops.aws/v2/workshops/9da471a0-266a-4d36-8596-e5934aeedd1f/en-US). Refer to the [Getting Started](https://catalog.us-east-1.prod.workshops.aws/v2/workshops/9da471a0-266a-4d36-8596-e5934aeedd1f/en-US/) guide for details.

## Repo structure

```bash
.
├── contentspec.yaml                  <-- Specifies the version of the content
├── README.md                         <-- This file.
├── static                            <-- Directory for static assets to be hosted alongside the workshop (ie. images, scripts, documents, etc) 
└── content                           <-- Directory for workshop content markdown
    └── index.en.md                   <-- At the root of each directory, there must be at least one markdown file
    └── introduction                  <-- Directory for workshop content markdown
        └── index.en.md               <-- Markdown file that would be render 
├── cdk                               <-- AWS CDK applications for deploying CI/CD pipeline, cfn-guard app, and IDE environment
    └── app                           <-- IaC and cfn-guard rules
    └── cicd                          <-- CICD pipeline to deploy IaC
    └── ide                           <-- Development environment includes bootstrap.sh. it installs all tools needed for this workshop
├── terraform                         <-- Terraform application using Regula for validation.
├── utils                             <-- Contains utilities that are useful for this workshop.
```

## Policy as Code Workshop Structure
The markdown source for the content in this [workshop](https://catalog.us-east-1.prod.workshops.aws/v2/workshops/9da471a0-266a-4d36-8596-e5934aeedd1f/en-US) is contained in the following folder:

* `static`: This folder contains static assets to be hosted alongside the workshop (ie. images, scripts, documents, etc) 
* `content`: This is the core workshop folder. This is generated as HTML and hosted for presentation for customers.
