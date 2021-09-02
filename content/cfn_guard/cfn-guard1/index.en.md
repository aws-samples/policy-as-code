---
title: "Security Group"
weight: 41
---

Policy as code must start with a set of rules that will enforce the policy. So let's imagine a simple scenario where our organization requires security groups to only allow ingress access to ports 443 and 22. As a start we should list out what our rules should check for to enforce this policy:

* Allow ingress traffic to port 443 and 22 only
* Allow no ingress traffic
* Disallow all other ingress traffic
* Only allow protocol tcp

Next we need a set of security groups that we can use to test the implementations of these rules. With cfn-guard we can create a unit test file that does exactly that. Let's put that unit test file together. Create a file named **sg_ingress_test.yaml** with the contents below:

```
- input:
    Resources: {}
  expectations:
    rules:
        check_security_group_ingress: SKIP
```
This is a dummy test meant to make sure that we have syntactically correct rules. We want to be familiar with cfn-guard and get it to run succesfully to start. Create a file named **sg_ingress.yaml** as specified below:

```
rule check_security_group_ingress {
  let sgs = Resources.*[ Type == 'AWS::EC2::SecurityGroups' ]
}
```

This rule doesn't do much other than assign security groups within a given template to the variable **sgs** We will be adding more to this as we add more unit tests. For now let's see if we can get our first unit test to pass:

```
cfn-guard test --rules-file sg_ingress.guard --test-data sg_ingress.guard
```

The output should look something like this:

```
PASS Expected Rule = check_security_group_ingress, Status = SKIP, Got Status = SKIP
```

Great, we now have a syntactically correct rule and unit test file. It's time to start developing our rules to enforce our organizations policy.

We will add the following contents to our existing **sg_ingress_test.guard** file:

```
- input:
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
                  ToPort: 80
                VpcId:
                    Ref: Vpc8378EB38
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_security_group_ingress: PASS
```

Here we have a security group that will allow ingress to port 443. This should fail when we run the test as we haven't written a rule to check this port. Let's run it and see what result we get:

```
cfn-guard test --rules-file sg_ingress.guard --test-data sg_ingress.guard
```

The results you should get looks like the following:

```
PASS Expected Rule = check_security_group_ingress, Status = SKIP, Got Status = SKIP
FAILED Expected Rule = check_security_group_ingress, Status = PASS, Got Status = SKIP
```

We now have a **FAILED Expected Rule** on the 2nd unit test. Instead of getting the expected status **PASS** we get **SKIP** because there are no rules for checking the ingress port number. Let's update **sg_ingress.guard** with the contents shown below:

```
rule check_security_group_ingress {
    let sgs = Resources.*[ Type == 'AWS::EC2::SecurityGroup' ]

    when %sgs !empty {
        %sgs {
            Properties {
                SecurityGroupIngress[*] {
                    FromPort == 443
                }
            }
        }
    }
}
```

Here we add a conditional for the security group and if we are given no security group resources we will skip. That is what the **when %sgs !empty** guards against. This should allow us to pass the first test. The rest of it is checking our properties, specifically the ingress port of the FromPort attribute. Running this again we should have passing unit tests:

```
cfn-guard test --rules-file sg_ingress.guard --test-data sg_ingress.guard
```

The output looks like this:

```
PASS Expected Rule = check_security_group_ingress, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_security_group_ingress, Status = PASS, Got Status = PASS
```

So far so good, however we've specified a single port. There is going to be a problem with port 22 which is permissible. Let's add that to our unit test (After you add this you should have 3 unit tests defined.):

```
- input:
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
                  ToPort: 80
                - CidrIp: 0.0.0.0/0
                  Description: Allow anyone to connect to port 80
                  FromPort: 22
                  IpProtocol: tcp
                  ToPort: 80
                VpcId:
                    Ref: Vpc8378EB38
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_security_group_ingress: PASS
```

Running this again:

```
cfn-guard test --rules-file sg_ingress.guard --test-data sg_ingress.guard
```

We should see something like:

```
PASS Expected Rule = check_security_group_ingress, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_security_group_ingress, Status = PASS, Got Status = PASS
FAILED Expected Rule = check_security_group_ingress, Status = PASS, Got Status = FAIL
```

Here the last test fails as expected because we haven't added a rule that will allow port 22. We should add this to our rules file **sg_ingress.guard**. Update the contents as show below:

```
rule check_security_group_ingress {
    let sgs = Resources.*[ Type == 'AWS::EC2::SecurityGroup' ]

    when %sgs !empty {
        %sgs {
            Properties {
                SecurityGroupIngress[*] {
                    FromPort in [443, 22]
                }
            }
        }
    }
}
```

Running our test again:

```
cfn-guard test --rules-file sg_ingress.guard --test-data sg_ingress.guard
```

We should see something like:

```
PASS Expected Rule = check_security_group_ingress, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_security_group_ingress, Status = PASS, Got Status = PASS
PASS Expected Rule = check_security_group_ingress, Status = PASS, Got Status = PASS
```

We should allow for security groups that don't have ingress ports defined at all. Let's see what happens when we add a test for that. Add the following test in your unit test file **sg_ingress_test.yaml** (you should have 4 unit tests after adding this one):

```
- input:
    Resources:
        TestSecurityGroup:
            Type: AWS::EC2::SecurityGroup
            Properties:
                GroupDescription: Allows port ingress port 80
                SecurityGroupIngress:
                    CidrIp: 0.0.0.0/0
                    Description: Allow anyone to connect to port 80
                    IpProtocol: tcp
                    ToPort: 80
                VpcId:
                    Ref: Vpc8378EB38
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_security_group_ingress: PASS
```

Again we run our unit tests:

```
cfn-guard test --rules-file sg_ingress.guard --test-data sg_ingress.guard
```

The output looks like this:

```
PASS Expected Rule = check_security_group_ingress, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_security_group_ingress, Status = PASS, Got Status = PASS
PASS Expected Rule = check_security_group_ingress, Status = PASS, Got Status = PASS
FAILED Expected Rule = check_security_group_ingress, Status = PASS, Got Status = FAIL
```

Our rule doesn't take into consideration security groups with no ingress port and so it fails. Let's add a rule to **sg_ingress.guard** that will check for that:

```
rule check_security_group_ingress {
    let sgs = Resources.*[ Type == 'AWS::EC2::SecurityGroup' ]

    when %sgs !empty {
        %sgs {
            Properties {
                SecurityGroupIngress[*] {
                    FromPort in [443, 22] OR
                    FromPort is empty
                }
            }
        }
    }
}
```

Running our unit tests:

```
cfn-guard test --rules-file sg_ingress.guard --test-data sg_ingress.guard
```

The output looks like this:

```
PASS Expected Rule = check_security_group_ingress, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_security_group_ingress, Status = PASS, Got Status = PASS
PASS Expected Rule = check_security_group_ingress, Status = PASS, Got Status = PASS
PASS Expected Rule = check_security_group_ingress, Status = PASS, Got Status = PASS
```

Finally as an exercise try to see if you can check that the protocol is tcp. Remember to write your unit test first and see if the test fails. Than add or update the rule to pass the test.

Below is a sample of a working unit test with a rule that checks for tcp:

File **sg_ingress_test.yaml**
```
- input:
    Resources: {}
  expectations:
    rules:
        check_security_group_ingress: SKIP
- input:
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
                  ToPort: 80
                VpcId:
                    Ref: Vpc8378EB38
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_security_group_ingress: PASS
- input:
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
                  ToPort: 80
                - CidrIp: 0.0.0.0/0
                  Description: Allow anyone to connect to port 80
                  FromPort: 22
                  IpProtocol: tcp
                  ToPort: 80
                VpcId:
                    Ref: Vpc8378EB38
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_security_group_ingress: PASS
- input:
    Resources:
        TestSecurityGroup:
            Type: AWS::EC2::SecurityGroup
            Properties:
                GroupDescription: Allows port ingress port 80
                SecurityGroupIngress:
                    CidrIp: 0.0.0.0/0
                    Description: Allow anyone to connect to port 80
                    IpProtocol: tcp
                    ToPort: 80
                VpcId:
                    Ref: Vpc8378EB38
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_security_group_ingress: PASS
- input:
    Resources:
        TestSecurityGroup:
            Type: AWS::EC2::SecurityGroup
            Properties:
                GroupDescription: Allows port ingress port 80
                SecurityGroupIngress:
                    CidrIp: 0.0.0.0/0
                    Description: Allow anyone to connect to port 80
                    FromPort: 443
                    IpProtocol: udp
                    ToPort: 80
                VpcId:
                    Ref: Vpc8378EB38
            Metadata:
                aws:cdk:path: foo/Counter/LB/SecurityGroup/Resource
  expectations:
    rules:
        check_security_group_ingress: FAIL
```

Rules **sg_ingress.guard**

```
rule check_security_group_ingress {
    let sgs = Resources.*[ Type == 'AWS::EC2::SecurityGroup' ]

    when %sgs !empty {
        %sgs {
            Properties {
                SecurityGroupIngress[*] {
                    IpProtocol in ['tcp']
                    FromPort in [443, 22] OR
                    FromPort empty
                }
            }
        }
    }
}
```


