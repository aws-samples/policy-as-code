---
title: "Security Group"
weight: 41
---

Policy as code starts with a set of rules that will enforce the policy. So let's imagine a simple policy where our organization is looking to only communicate with secure protocols such as https and ssh. A policy might be stated like this:

*All network accessible services should only use protocols https or ssh. Network services should only be accessible via corporate network IP address spaces.*

As a start we can use AWS Security Group resources since this is a primary mechanism to enforce network level access in the cloud. Our rules might look like the following:

* Allow ingress traffic to port 443 and/or 22 only
* Disallow all other ingress traffic
* Allow only CIDR ranges 10.0.0.0/16
* Only allow protocol tcp

Next we need provide cloudformation snippets that test the implementations of these rules. Create a file named **sg_ingress_test.yaml** with the contents below:

```
- name: Check for a empty list of security groups
  input:
    Resources: {}
  expectations:
    rules:
        check_sgs_empty: PASS
```
This initial unit test will get us started. It gives a cloudformation snippet that has an empty **Resource** and a rule called check_sgs_empty that we expect to evaluate to **PASS**. We haven't written the rule check_sgs_empty but we clearly understand that in order for this test to pass, it needs to evaluate sgs (Which is a variable that isn't defined yet but meant to represents a list of security groups) as empty. We can do that by creating a file named **sg_ingress.guard** as specified below:

```
let sgs = Resources.*[ Type == 'AWS::EC2::SecurityGroup' ]
rule check_sgs_empty {
    %sgs empty
}
```
The first line queries **Resources** looking for all AWS::EC2::SecurityGroup that are specified. The rule check_sgs_empty returns a PASS if %sgs is empty. Let's see if we can get our first unit test to pass:

```
cfn-guard test -r sg_ingress.guard -t sg_ingress_test.yaml
```

The output should look something like this:

```
Test Case #1
Name: "Check for a empty list of security groups"
  PASS Rules:
    check_sgs_empty: Expected = PASS, Evaluated = PASS
```

Why did this rule PASS? Because the expectation is to **PASS**. There are other outcomes like **FAIL** or **SKIP** that we can set for expected. Even if you have a rule that evaluates to **PASS** but you expected it to **FAIL** or **SKIP** it will fail the test case. At this point we should have a syntactically correct rule and unit test file. Congrats! You've written your first passing unit test. It's time to start writing our rules to enforce our policy.

We will **ADD** the following contents to our existing unit file **sg_ingress_test.yaml**:
```
- name: Security group with single to/from port 443
  input:
    Resources:
        TestSecurityGroup:
            Type: AWS::EC2::SecurityGroup
            Properties:
                GroupDescription: Allows ngress port per policy
                SecurityGroupIngress:
                - CidrIp: 10.0.0.0/16
                  Description: Allow anyone to connect to port 443
                  FromPort: 443
                  IpProtocol: tcp
                  ToPort: 443
                VpcId:
                    Ref: VpcABCDEF
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_sgs_empty: FAIL
        check_security_group_ingress: PASS
```

Here we have a security group that will allow ingress to port 443.

Also we need to **ADD** this rule to our rule file **sg_ingress.guard**:
```
rule check_security_group_ingress {
    %sgs empty
}
```
This should fail when we run the test as we are expecting to have an empty list of security groups. It will not be empty because our test has a single resource which is a security group.

Let's run it and see what result we get:

```
cfn-guard test -r sg_ingress.guard -t sg_ingress_test.yaml
```

The results you should get looks like the following:

```
Test Case #1
Name: "Check for a empty list of security groups"
  No Test expectation was set for Rule check_security_group_ingress
  PASS Rules:
    check_sgs_empty: Expected = PASS, Evaluated = PASS

Test Case #2
Name: "Security Group with single to/from port 443"
  FAILED Rules:
    check_security_group_ingress: Expected = PASS, Evaluated = FAIL
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
```

We now have a **FAILED Expected Rule** on the 2nd test case. Instead of getting the expected status **PASS** we get **FAIL** because our rule is expecting an empty list of security groups. Let's **UPDATE** our rules file **sg_ingress.guard** with the contents shown below:

```
rule check_security_group_ingress {
    when %sgs !empty {
        %sgs {
            Properties {
                SecurityGroupIngress[*] {
                    FromPort == 443
                    ToPort == 443
                    IpProtocol exists
                    IpProtocol == 'tcp'
                }
            }
        }
    }
}
```

Here we add a conditional for the security group and if we are given no security group resources this rule will be skipped. That is what the line **when %sgs !empty** guards against. This should allow us to pass the first test. Note that we use the [*] to denote a list or array of SecurityGroupIngress objects. We also check the properties of any of the SecurityGroupIngress objects and if any of them don't match the properties we are expecting the rule will evaluate to **FAIL**. Running this again we should have passing unit tests:

```
cfn-guard test -r sg_ingress.guard -t sg_ingress_test.yaml
```

The output looks like this:

```
Test Case #1
Name: "Check for a empty list of security groups"
  No Test expectation was set for Rule check_security_group_ingress
  PASS Rules:
    check_sgs_empty: Expected = PASS, Evaluated = PASS

Test Case #2
Name: "Security Group with single to/from port 443"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS
```

So far so good. However we've specified a single port and this rule will fail if a SecurityGroupIngress specifies to/from port 22 which is permissible. Let's **ADD** that to our unit test (After you add this you should have 3 unit tests defined.):

```
- name: Security group that specifies 443 and 22
  input:
    Resources:
        TestSecurityGroup:
            Type: AWS::EC2::SecurityGroup
            Properties:
                GroupDescription: Allows ingress port per policy
                SecurityGroupIngress:
                - CidrIp: 10.0.0.0/16
                  Description: Allow anyone to connect to port 443
                  FromPort: 443
                  IpProtocol: tcp
                  ToPort: 443
                - CidrIp: 10.0.0.0/16
                  Description: Allow anyone to connect to port 22
                  FromPort: 22
                  IpProtocol: tcp
                  ToPort: 22
                VpcId:
                    Ref: Vpc8378EB38
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_sgs_empty: FAIL
        check_security_group_ingress: PASS
```

Running this again:

```
cfn-guard test -r sg_ingress.guard -t sg_ingress_test.yaml
```

We should see something like:

```
Test Case #1
Name: "Check for a empty list of security groups"
  No Test expectation was set for Rule check_security_group_ingress
  PASS Rules:
    check_sgs_empty: Expected = PASS, Evaluated = PASS

Test Case #2
Name: "Security group with single to/from port 443"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #3
Name: "Security group that specifies to/from port 443 and 22"
  FAILED Rules:
    check_security_group_ingress: Expected = PASS, Evaluated = FAIL
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
```

Here the last test fails as expected because we haven't added a rule that will allow port 22. We should **UPDATE** this check to our rules file **sg_ingress.guard**:

```
rule check_security_group_ingress {
    when %sgs !empty {
        %sgs {
            Properties {
                SecurityGroupIngress[*] {
                    FromPort in [443, 22]
                    ToPort in [443, 22]
                    IpProtocol exists
                    IpProtocol == 'tcp'
                }
            }
        }
    }
}
```

Running our test again:

```
cfn-guard test -r sg_ingress.guard -t sg_ingress_test.yaml
```

We should see something like:

```
Test Case #1
Name: "Check for a empty list of security groups"
  No Test expectation was set for Rule check_security_group_ingress
  PASS Rules:
    check_sgs_empty: Expected = PASS, Evaluated = PASS

Test Case #2
Name: "Security group with single to/from port 443"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #3
Name: "Security group that specifies to/from port 443 and 22"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS
```

Now let's add a port that would violate our policy in our unit test. Add the following test in your unit test file **sg_ingress_test.yaml** (you should have 4 unit tests after adding this one):

```
- name: Security group with to/from port 80
  input:
    Resources:
        TestSecurityGroup:
            Type: AWS::EC2::SecurityGroup
            Properties:
                GroupDescription: Allows port ingress port 80
                SecurityGroupIngress:
                    CidrIp: 10.0.0.0/16
                    Description: Allow anyone to connect to port 80
                    IpProtocol: tcp
                    ToPort: 80
                    FromPort: 80
                VpcId:
                    Ref: Vpc8378EB38
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_sgs_empty: FAIL
        check_security_group_ingress: FAIL
```

Again we run our unit tests:

```
cfn-guard test -r sg_ingress.guard -t sg_ingress_test.yaml
```

The output looks like this:

```
Test Case #1
Name: "Check for a empty list of security groups"
  No Test expectation was set for Rule check_security_group_ingress
  PASS Rules:
    check_sgs_empty: Expected = PASS, Evaluated = PASS

Test Case #2
Name: "Security Group with single to/from port 443"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #3
Name: "Security group that specifies to/from port 443 and 22"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #4
Name: "Security group with to/from port 80"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = FAIL, Evaluated = FAIL
```

Excellent it seems that our rules would catch a CF template that tried to provision a security group allowing inbound access to port 80 which is a violation of our stated policies. However are we testing for CIDR ranges? Let's add a test to do that:

```
- name: Security Group with to/from port 443 from anywhere
  input:
    Resources:
        TestSecurityGroup:
            Type: AWS::EC2::SecurityGroup
            Properties:
                GroupDescription: Allows port ingress port 80
                SecurityGroupIngress:
                - CidrIp: 0.0.0.0/0
                  Description: Allow anyone to connect to port 80
                  FromPort: 443
                  IpProtocol: tcp
                  ToPort: 443
                VpcId:
                    Ref: VpcABCDEF
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_sgs_empty: FAIL
        check_security_group_ingress: FAIL
```

Once we update our **sg_ingress_test.yaml** we will run our command:

```
cfn-guard test -r sg_ingress.guard -t sg_ingress_test.yaml
```

The results will look like this:

```
Test Case #1
Name: "Check for a empty list of security groups"
  No Test expectation was set for Rule check_security_group_ingress
  PASS Rules:
    check_sgs_empty: Expected = PASS, Evaluated = PASS

Test Case #2
Name: "Security Group with single to/from port 443"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #3
Name: "Security group that specifies to/from port 443 and 22"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #4
Name: "Security group with to/from port 80"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = FAIL, Evaluated = FAIL

Test Case #5
Name: "Security Group with to/from port 443 from anywhere"
  FAILED Rules:
    check_security_group_ingress: Expected = FAIL, Evaluated = PASS
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
```
Here we have **FAILED Rules** from check_security_group_ingress. Although it was expected to **FAIL** because we are using a wide open CIDR 0.0.0.0/0 it evaluated as a **PASS**. This isn't the expected behavior because our rules should **FAIL** when a CIDR other than 10.0.0.0/16 is given. Currently our rules do not check CIDR ranges at all. Let's **UPDATE** our rules file **sg_ingress.guard**:
```
rule check_security_group_ingress {
    when %sgs !empty {
        %sgs {
            Properties {
                SecurityGroupIngress[*] {
                    CidrIp == '10.0.0.0/16'
                    FromPort in [443, 22]
                    ToPort in [443, 22]
                    IpProtocol exists
                    IpProtocol == 'tcp'
                }
            }
        }
    }
}
```
With our added property check for CidrIp the output should look like this:

```
Test Case #1
Name: "Check for a empty list of security groups"
  No Test expectation was set for Rule check_security_group_ingress
  PASS Rules:
    check_sgs_empty: Expected = PASS, Evaluated = PASS

Test Case #2
Name: "Security Group with single to/from port 443"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #3
Name: "Security group that specifies to/from port 443 and 22"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #4
Name: "Security group with to/from port 80"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = FAIL, Evaluated = FAIL

Test Case #5
Name: "Security Group with to/from port 443 from anywhere"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = FAIL, Evaluated = FAIL
```
Let's see if our rules would successfully catch a protocol violation. Add another unit test to **sg_ingress_test.yaml**:
```
- name: Security Group with udp ingress 443
  input:
    Resources:
        TestSecurityGroup:
            Type: AWS::EC2::SecurityGroup
            Properties:
                GroupDescription: Allows port ingress port 80
                SecurityGroupIngress:
                - CidrIp: 10.0.0.0/16
                  Description: Allow anyone to connect to port 80
                  FromPort: 443
                  IpProtocol: udp
                  ToPort: 443
                VpcId:
                    Ref: VpcABCDEF
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_sgs_empty: FAIL
        check_security_group_ingress: FAIL
```
And the result should look like this:
```
Test Case #1
Name: "Check for a empty list of security groups"
  No Test expectation was set for Rule check_security_group_ingress
  PASS Rules:
    check_sgs_empty: Expected = PASS, Evaluated = PASS

Test Case #2
Name: "Security Group with single to/from port 443"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #3
Name: "Security group that specifies to/from port 443 and 22"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = PASS, Evaluated = PASS

Test Case #4
Name: "Security group with to/from port 80"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = FAIL, Evaluated = FAIL

Test Case #5
Name: "Security Group with to/from port 443 from anywhere"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = FAIL, Evaluated = FAIL

Test Case #6
Name: "Security Group with udp ingress 443"
  PASS Rules:
    check_sgs_empty: Expected = FAIL, Evaluated = FAIL
    check_security_group_ingress: Expected = FAIL, Evaluated = FAIL
```
Fantastic, it seems our rules would catch CF templates attempting to use udp as the protocol.

Let's review the rules that will enforce our policy:

* Allow ingress traffic to port 443 and/or 22 only
* Disallow all other ingress traffic
* Allow only CIDR ranges 10.0.0.0/16
* Only allow protocol tcp

We have written 6 test cases that test each of these rules. Congratulations! You are well on your way to becoming a policy as code ninja.
