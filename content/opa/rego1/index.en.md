---
title: "Security Group Example"
weight: 43
---

### Allow only secure ports
Let's start with a simple CF template snippet that creates a security group. Create a file **template.json** that contains the content below:

````
    "Resources": {
        "CounterLBSecurityGroup63C1AB9D": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Automatically created Security Group for ELB fooCounterLBAEF24CE8",
                "SecurityGroupIngress": [{
                    "CidrIp": "0.0.0.0/0",
                    "Description": "Allow from anyone on port 80",
                    "FromPort": 80,
                    "IpProtocol": "tcp",
                    "ToPort": 80
                }],
                "VpcId": {
                    "Ref": "Vpc8378EB38"
                }
            },
            "Metadata": {
                "aws:cdk:path": "foo/Counter/LB/SecurityGroup/Resource"
            }
        }
    }
````
{{% notice note %}}
You may notice this security group allows wide open access **0.0.0.0/0** on non-secure port 80.
{{% /notice %}}

We want to limit the incoming port of the security group to allow access only to port 443 SSL. Create a new file **check-sg-limit-secured-port.rego** with the contents below:
```
package security_group

default deny_non_secured_ports = true

deny_non_secured_ports = false  {
    some resource,j
    input.Resources[resource].Type == "AWS::EC2::SecurityGroup"
    input.Resources[resource].Properties.SecurityGroupIngress
    input.Resources[resource].Properties.SecurityGroupIngress[j].FromPort == 443
}
```
We can test the rule by running the below command:
```
opa eval -i template.json -d check-sg-limit-secured-port.rego data.security_group.deny_non_secured_ports --explain=notes
```
Results:
```
{
  "result": [
    {
      "expressions": [
        {
          "value": true,
          "text": "data.security_group.deny_non_secured_ports",
          "location": {
            "row": 1,
            "col": 1
          }
        }
      ]
    }
  ]
}
```
Now change the value in the CF template to 443 and rerun. Results:
```
{
  "result": [
    {
      "expressions": [
        {
          "value": false,
          "text": "data.security_group.deny_non_secured_ports",
          "location": {
            "row": 1,
            "col": 1
          }
        }
      ]
    }
  ]
}
```
You can see the value of the expression is now returning "false" to deny_non_secured_ports.

#### Explanation
Rego language build documents on evaluation which contains objects. The evaluation of a rule can be returned as true or false. We can also build more data structures that will be returned from our rules. For example we can ask rego to return which security group violated our rule. We will explore this in the next example.


1. The rule start with a **package** declaration which is the namespace for the current Rego code. We use this namespace as part of our execution command line. Also consider that when running multiple rego files against a stack it is useful to adopt proper namespace so rules can be abstracted and join together(import) statement.
2. Next we define a variable deny_non_secured_ports with a default value of "true"
3. Next, we create a rule - which if true will return false
   * A rule is true when all the statements evaluate to true
   * Implicitly a line is a logical AND within a rule block
4. The content of the rule exist in the curly bracket
5. The keyword **resource** define an enumerable variables - this means rego will try every possible combination/permutation for that variable to find at least one true statement
6. Next we have a series of statement which we condition as "only move to the next statement if the current one is true". when we have collections and we want rego to attempt to find a match with use the square bracket and the variable within

{{% notice tip %}}
Change the execution line part from "data.security_group.deny_non_secured_ports" to: "data.security_group" - Rego will return all the elements, and their evaluated result(document) - this is useful for debugging and checking multiple statements.
{{% /notice %}}
{{% notice tip %}}
In order to see you can use the content of a variable you can use the "trace" command(while explain=notes/full is used) i.e: trace(sprintf("resource_name=%s", [resource])) 
{{% /notice %}}


### No shared security group without exemption
Let's explore a more complex example. Assume we wish every EC2 instance to be created along with a security group rather than referencing an existing one. Additionally, we allow for exemptions through a tag in the metadata part of the resource.

Update our file **template.json** with the contents below:
```
{
          "Resources": {
               "NewSecurityGroupACA21D0A": {
                    "Type": "AWS::EC2::SecurityGroup",
                    "Properties": {
                      "GroupDescription": "Allow ssh access to ec2 instances",
                      "SecurityGroupEgress": [
                        {
                          "CidrIp": "0.0.0.0/0",
                          "Description": "Allow all outbound traffic by default",
                          "IpProtocol": "-1"
                        }
                      ],
                      "SecurityGroupIngress": [
                        {
                          "CidrIp": "0.0.0.0/0",
                          "Description": "allow ssh access from the world",
                          "FromPort": 22,
                          "IpProtocol": "tcp",
                          "ToPort": 22
                        }
                      ],
                      "VpcId": {
                        "Ref": "TheVPC92636AB0"
                      }
                    },
                    "Metadata": {
                      "aws:cdk:path": "CdkSecurityGroupStack/NewSecurityGroup/Resource"
                    }
                },
                "myInstanceUsingNewSG": {
                  "Type": "AWS::EC2::Instance",
                  "Properties": {
                    "ImageId": " ami-0f5dbc86dd9cbf7a8",
                    "InstanceType": "t2.micro",
                    "NetworkInterfaces": [
                      {
                        "DeviceIndex": "0",
                        "SubnetId": {
                          "Ref": "TheVPCapplicationSubnet1Subnet2149DB21"
                        }
                      }
                    ],
                    "SecurityGroupIds": [
                      {
                        "Fn::GetAtt": [
                          "NewSecurityGroupACA21D0A",
                          "GroupId"
                        ]
                      }
                    ],
                    "Tags": [
                      {
                        "Key": "Name",
                        "Value": "my-new-ec2-myInstanceUsingNewSG"
                      }
                    ]
                  },
                  "Metadata": {
                    "aws:cdk:path": "CdkSecurityGroupStack/myInstanceUsingNewSG"
                  }
                },
                "myInstanceUsingExistingSG": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                      "ImageId": " ami-0f5dbc86dd9cbf7a8",
                      "InstanceType": "t2.micro",
                      "NetworkInterfaces": [
                        {
                          "DeviceIndex": "0",
                          "SubnetId": {
                            "Ref": "TheVPCapplicationSubnet1Subnet2149DB21"
                          }
                        }
                      ],
                      "SecurityGroupIds": [
                        "sg-12345"
                      ],
                      "Tags": [
                        {
                          "Key": "Name",
                          "Value": "my-new-ec2-myInstanceUsingExistingSG"
                        }
                      ]
                    },
                    "Metadata": {
                      "aws:cdk:path": "CdkSecurityGroupStack/myInstanceUsingExistingSG",
                      "SharedSecurityGroup": true
                    }
                  }
        }
    }
```

What are we creating in the above stack?

1. The template contains one security group and two EC2 instance resources.
1. The first instance is using the newly created security group above, however the second instance is using a reference to a security group not in this stack. (i.e **sg-12345**)
1. For the second instance we provide additional metadata key "SharedSecurityGroup" as an exception to allow referring a security group that is not created in this stack.

Let's write a rules to implement this logic. Create a new file **check-no-shared-sg.rego** and paste the content below:
```
package security_group

resource_type = "AWS::EC2::SecurityGroup"

default allow = true

allow = false {
    count(violation) > 0
}

violation[retVal] {
    non_compliant_resources = all_sg_resources[_] - compliant_sg - compliant_sg_get - compliant_sg_ref
#    trace(sprintf("all_sg_resources=%s", [all_sg_resources]))
#    trace(sprintf("compliant_sg=%s", [compliant_sg]))
#    trace(sprintf("compliant_sg_get=%s", [compliant_sg_get]))
#    trace(sprintf("compliant_sg_ref=%s", [compliant_sg_ref]))

    count(non_compliant_resources) > 0
    retVal := { msgJson |
        sg = non_compliant_resources[_]
        msgJson := {
            "resource": sg,
            "message": "The Security group resource is not compliant, please fix the useage of this security group and try again."
        }
    }
}

# This partial rule check for security group which are strings - direct reference and had not set a metadata of SharedSecurityGroup
compliant_sg[resource] {
    some resource
    input.Resources[resource].Properties.SecurityGroupIds
    is_string(input.Resources[resource].Properties.SecurityGroupIds[0])
    input.Resources[resource].Metadata.SharedSecurityGroup
}

# This partial rule check for referred security group and make sure it's created on the same declared stack as a resource
compliant_sg_get[resource] {
    some resource
    input.Resources[resource].Properties.SecurityGroupIds
    logical_group_names := get_cf_logical_resource_names(input.Resources[resource].Properties.SecurityGroupIds, "GroupId")
    #validating the logical security group names exist in the template as security group
    validate_resource_exists(logical_group_names[_], "AWS::EC2::SecurityGroup")
    count(logical_group_names)>0
}

compliant_sg_ref[resource] {
    some resource
     input.Resources[resource].Properties.SecurityGroups
     logical_group_names := get_cf_ref_logical_resource_names(input.Resources[resource].Properties.SecurityGroups)
     #validating the Reference is actually mapped to a security group
     validate_resource_exists(logical_group_names[_], "AWS::EC2::SecurityGroup")
     count(logical_group_names) > 0
}

all_sg_resources[resource] {
    some resource
    resource = (all_sg_resources_SecurityGroupIds | all_sg_resources_SecurityGroups)
}

all_sg_resources_SecurityGroupIds[resource] {
    some resource
    input.Resources[resource].Properties.SecurityGroupIds
}

all_sg_resources_SecurityGroups[resource] {
    some resource
    input.Resources[resource].Properties.SecurityGroups
}

validate_resource_exists(resource_name, resource_type)
{
    some resource
    input.Resources[resource].Type == resource_type
    resource == resource_name
}

# Returns CF logical resource names from an array of Fn::GetAtt
get_cf_logical_resource_names(objects, attribute) = resource_names
{
    some i
    resource_names := {
        return_val |
        return_val := get_cf_FnGetAtt_logical_resource_name(objects[i], attribute)
    }
    #trace(sprintf("ret_items=%v", [resource_names]))
}

# Returns CF logical resource names from an array of Ref
get_cf_ref_logical_resource_names(objects) =  resource_names
{
    some i
    resource_names := {
        return_val |
        obj = objects[i]
        obj["Ref"]
        return_val := obj["Ref"]
    }
    #trace(sprintf("resource_names=%v", [resource_names]))
}

# Returns CF logical resource name for Fn::GetAtt
get_cf_FnGetAtt_logical_resource_name(obj, attribute) = resource_name
{
    value = obj["Fn::GetAtt"]
    trace(sprintf("value=%v", [value]))
    value[1] == attribute
    resource_name := value[0]
    #trace(sprintf("resource_name=%v", [resource_name]))
}
```
Let's review the content and explain some new declaration we use.

In this example notice there are multiple rules; violation, compliant_sg_get, compliant_sg_get, compliant_sg_ref, all_sg_resources etc.

Rego support partial rules which allows you to make the logic more modular. i.e: all_sg_resources_Security_group simply returns a list of all resources which make use of SecurityGroup property.

In addition, we bring the notion of "compliant" vs "non-compliant" resources. We derive the non-compliant resources by taking all the applicable security group resources and removing the resources which are compliant. Then we count if there are any noncompliant resources.

Finally, we introduce an example for functions validate_resource_exists, get_cf_ref_logical_resource_names, and get_cf_logical_resource_names. We can use function to calculate complex process on a given argument/resource or provide validation.
 
{{% notice tip %}}
You may use "False" statement in a rule in order to look at the trace output and see what is being calculated .
{{% /notice %}}
Let's run the rule:
```
opa eval -i template.json -d check-no-shared-sg.rego data.security_group.allow

```
Result
```
{
  "result": [
    {
      "expressions": [
        {
          "value": true,
          "text": "data.security_group.allow",
          "location": {
            "row": 1,
            "col": 1
          }
        }
      ]
    }
  ]
```
Our allow rule returns true,
<br/>

{{% notice tip %}}
you can run the command below to view all the document rules evaluation - this is very useful to understand what has been calculated in every rule
{{% /notice %}}

```
opa eval -i template.json -d check-no-shared-sg.rego data.security_group
```
Now let's check what happen when we make changes which will create non-compliant resources. Make the following changes below: 

1. Change "SharedSecurityGroup": true to false
1. Remove the property "SharedSecurityGroup": true from the metadata
1. Delete the NewSecurityGroupACA21D0A security group from the stack
1. Change the reference from: "Fn::GetAtt": ["NewSecurityGroupACA21D0A",..] to: "Fn::GetAtt": ["WrongReferenceSG",..]

Don't forget to add --explain=notes to see the appropriate message from the noncompliance resource and run with:
```
opa eval -i template.json -d check-no-shared-sg.rego data.security_group --explain=notes
```
