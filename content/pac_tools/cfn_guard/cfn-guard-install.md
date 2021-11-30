---
title: "Installation"
weight: 10
---

This section provides instruction on installation of cfn-guard.

::alert[ **NOTE**: If you are attending an AWS Hosted Event to do this workshop OR you ran the bootstrap.sh script earlier, this step is not necessary! Only do this step if you elected not to run the bootstrap.sh script.]

1. To install the latest version of cfn-guard on Cloud9, do the following:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/dchakrav-github/cloudformation-guard/main/install-guard.sh | VERSION=v2.1.0-pre-rc1 sh
   ```
1. Either run the statement below or add that into .bash_profile:
   ```bash
   export PATH=${PATH}:~/.guard/bin
   ```
