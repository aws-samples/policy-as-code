---
title: "Cloud9 Environment Creation"
weight: 20
---

AWS Cloud9 is a cloud-based integrated development environment (IDE) that lets you write, run, and debug your code with 
just a browser. It includes a code editor, debugger, and terminal. Cloud9 comes pre-packaged with essential tools for 
popular programming languages, the AWS Command Line Interface (CLI), docker CLI, git and much more pre-installed so 
you don’t need to install files or configure your laptop for this workshop. This workshop requires use of *nix environment 
since it uses bash scripts as part of the labs. Cloud9 runs on an Amazon EC2 instance with Amazon Linux 2 by default. 
Your Cloud9 environment will have access to the same AWS resources as the user with which you logged into the AWS 
Management Console.

### Setup the Cloud9 Development Environment

- Go to the AWS Management Console, search for cloud9 in search box and then select **Cloud9**.

   ![Cloud9 Search](/static/images/prerequisites/cloud9-aws-console-search.png)

- Click **Create environment**.

   ![Cloud9 Start Create](/static/images/prerequisites/cloud9-start-create-env.png)

- Enter `policy-as-code-workshop` into **Name** and optionally provide a **Description**.

   ![Cloud9 Environment Name](/static/images/prerequisites/cloud9-env-name.png)

- Click **Next step**.

- In **Environment settings** select **Create a new no-ingress EC2 instance for environment (access via Systems Manager)**, **m5.large**, **Amazon Linux 2 (recommended)** EC2 instance which will be paused after **30 minutes** of inactivity.

   ![Cloud9 Configure Settings](/static/images/prerequisites/cloud9-configure-settings.png)

- Click **Next step**.

- Review the environment settings and click **Create environment**. It will take several minutes for your environment to be provisioned and prepared.

   ![Cloud9 Create Environment](/static/images/prerequisites/cloud9-create-env.png)

- Once ready, your IDE will open to a `Welcome` tab and `AWS Toolkit -Quick Start` tab. The central panel of the IDE has two parts:  a text/code editor in the upper half, and a terminal window in the lower half. Below the welcome screen in the editor, you should see a terminal prompt similar to the following (you may need to scroll down below the welcome screen to see it):

   ![Terminal](/static/images/prerequisites/sm-setup-cloud9-terminal.png)

When it comes up, customize the environment by closing the welcome and other tabs by clicking the **x** symbol in each tab. 
To create a new text/code file, just click the **+** symbol in the tabs section of the editor part of the IDE.

- Closing the **Welcome tab** and **AWS Toolkit -Quick Start**
   ![c9before](/static/images/prerequisites/cloud9-1.png)
- Opening a new **terminal** tab in the main work area
   ![c9newtab](/static/images/prerequisites/cloud9-2.png)
- Closing the lower work area
   ![c9newtab](/static/images/prerequisites/cloud9-3.png)
- Your workspace should now look like this
   ![c9after](/static/images/prerequisites/cloud9-4.png)
