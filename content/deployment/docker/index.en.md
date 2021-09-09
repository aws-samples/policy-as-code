---
title: "Docker Images"
weight: 62
---

In this section, we will build docker images that can be used to scan our code inside pipelines

Points to consider:
- This piece can also be done in a pipeline, but it means that the code for the docker image needs to sit in another repo
- OpenPolicy Agent includes it's own [DockerImage](https://hub.docker.com/r/openpolicyagent/opa/) on DockerHub
## Building a custom docker image
#### Dockerfile
```Dockerfile
FROM python:alpine3.14

RUN apk --update add --no-cache cargo
RUN cargo install cfn-guard
ENV PATH "/root/.cargo/bin:${PATH}"
RUN pip3 install cfn-lint
```
```bash
docker build -t pac .
```