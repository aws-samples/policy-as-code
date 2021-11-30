---
title: "Installing Checkov"
weight: 31
---

::alert[ **NOTE**: If you are attending an AWS Hosted Event to do this workshop OR you ran the bootstrap.sh script earlier, this step is not necessary! Only do this step if you elected not to run the bootstrap.sh script.]

## Install Checkov CLI

### Python

```bash
pip3 install checkov
```

### Docker

- [DockerHub](https://hub.docker.com/r/bridgecrew/checkov)

### Verify Checkov Installation

Check to see that you can run the cli for checkov on your terminal.

```
$ checkov




       _               _
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V /
  \___|_| |_|\___|\___|_|\_\___/ \_/

By bridgecrew.io | version: 2.0.390
Update available 2.0.390 -> 2.0.410
Run pip3 install -U checkov to update

```
