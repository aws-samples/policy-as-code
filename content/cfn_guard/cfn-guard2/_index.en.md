+++
title = "RDS"
weight = 42
+++

Starting with a policy, we want a AWS RDS instance that is not overly sized and uses a specific instance type, no accessiblity from the internet, and has encryption at rest enabled. Let's write a few rules that would enforce this policy:
* DBInstance class must use db.m6.<size> where size can be large, xlarge, and 2xlarge
* DBInstance is not publicly accessible
* DBInstance has encryption enabled

Let's start out with a unit test file called **rds_compliance_test.yaml** and add a simple unit test:

```
- input:
    Resources: {}
  expectations:
    rules:
      rds_compliance_check: SKIP
```

Also let's create the bare minimum rules file need to pass this test. Create a file named **rds_compliance.guard** with contents below:

```
rule rds_compliance_check {
  let rds = Resources.*[ Type == 'AWS::RDS::DBInstance' ]
}
```

Let's run the unit test:

```
cfn-guard test --rules-file rds_compliance.guard --test-data rds_compliance_test.yaml
```

The result:

```
PASS Expected Rule = rds_compliance_check, Status = SKIP, Got Status = SKIP
```

We've validated that we have the correct syntax for both unit and rule file. Let's look at the rules we've written above and see what test we can create.

Update the unit test file **rds_compliance_test.yaml** with contents below (we should have two unit tests after this update, replace the original unit test):

```
- input:
    Resources: {}
  expectations:
    rules:
      check_db_instance_type: SKIP
      check_public_accessibility: SKIP
      check_storage_encryption: SKIP
- input:
    Resources:
      Rds00:
        Type: AWS::RDS::DBInstance
        Properties:
          DBInstanceClass: db.m6.large
          AllocatedStorage: 100
          Engine: oracle-se2
          EngineVersion: 19.0.0.0.ru-2020-04.rur-2020-04.r1
          MasterUsername: syscdk
          MasterUserPassword: x8204fsfxx
          PubliclyAccessible: true
          StorageType: gp2
          StorageEncrypted: true
        Metadata:
          aws:cdk:path: CdkRDSStack/Instance/Resource
  expectations:
    rules:
      check_db_instance_type: PASS
      check_public_accessibility: PASS
      check_storage_encryption: PASS
```

Here we have a unit test that we will use three cfn-guard rules to check specific attributes of our RDS instance. Let's update our rules file so that we can accomodate these three cfn-guard rules. We don't have check_db_instance_types, check_public_accessibility, and check_storage_encryption defined so let's add them. Update **rds_compliance.guard** with the contents below:

```
# add a global rds variable that we will use with all of our rules in this file
let rds = Resources.*[
    Type == 'AWS::RDS::DBInstance'
]

rule check_db_instance_type when %rds !empty {
    %rds {
        Properties empty
    }
}

rule check_public_accessibility when %rds !empty {
    %rds {
        Properties empty
    }
}

rule check_storage_encryption when %rds !empty {
    %rds {
        Properties empty
    }
}
```

Run the unit test:

```
cfn-guard test --rules-file rds_compliance.guard --test-data rds_compliance_test.yaml
```

The result should be:

```
PASS Expected Rule = check_db_instance_type, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_public_accessibility, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_storage_encryption, Status = SKIP, Got Status = SKIP
FAILED Expected Rule = check_db_instance_type, Status = PASS, Got Status = FAIL
FAILED Expected Rule = check_public_accessibility, Status = PASS, Got Status = FAIL
FAILED Expected Rule = check_storage_encryption, Status = PASS, Got Status = FAIL
```

We've created three rules that simply check if the properties are empty. As expected they fail on the 2nd unit test, however we will update the rules to pass these checks. Let's start with the check_db_instance_type. We need to ensure that only a specific RDS instance type is used with a specific size. Let's update the rules file **rds_compliance.guard** with the contents below:

```
# add a global rds variable that we will use with all of our rules in this file
let rds = Resources.*[
    Type == 'AWS::RDS::DBInstance'
]

rule check_db_instance_type when %rds !empty {
    %rds {
        Properties {
          DBInstanceClass in ['db.m6.large', 'db.m6.xlarge', 'db.m6.2xlarge']
        }
    }
}

rule check_public_accessibility when %rds !empty {
    %rds {
        Properties empty
    }
}

rule check_storage_encryption when %rds !empty {
    %rds {
        Properties empty
    }
```

Let's run the unit test:

```
cfn-guard test --rules-file rds_compliance.guard --test-data rds_compliance_test.yaml
```

The result:

```
PASS Expected Rule = check_db_instance_type, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_public_accessibility, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_storage_encryption, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_db_instance_type, Status = PASS, Got Status = PASS
FAILED Expected Rule = check_public_accessibility, Status = PASS, Got Status = FAIL
FAILED Expected Rule = check_storage_encryption, Status = PASS, Got Status = FAIL
```

We have two failing tests but we will fix them shortly. Next let's look into checking for public accessbility. We can add a check for the property **StorageEncrypted** Let's update our rule **rds_compliance.guard** as specified below:

```
# add a global rds variable that we will use with all of our rules in this file
let rds = Resources.*[
    Type == 'AWS::RDS::DBInstance'
]

rule check_db_instance_type when %rds !empty {
    %rds {
        Properties {
          DBInstanceClass in ['db.m6.large', 'db.m6.xlarge', 'db.m6.2xlarge']
        }
    }
}

rule check_public_accessibility when %rds !empty {
    %rds {
        Properties {
            PubliclyAccessible exists
        }
    }
}

rule check_storage_encryption when %rds !empty {
    %rds {
        Properties empty
    }
}
```

Running the unit test:

```
cfn-guard test --rules-file rds_compliance.guard --test-data rds_compliance_test.yaml
```

The results:

```
PASS Expected Rule = check_db_instance_type, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_public_accessibility, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_storage_encryption, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_db_instance_type, Status = PASS, Got Status = PASS
PASS Expected Rule = check_public_accessibility, Status = PASS, Got Status = PASS
FAILED Expected Rule = check_storage_encryption, Status = PASS, Got Status = FAIL
```

We have one last test to fix. The last test is similiar to the public accessiblity property. Next let's add the StorageEncrypted property to the **rds_compliance.guard** as specified below:

```
# add a global rds variable that we will use with all of our rules in this file
let rds = Resources.*[
    Type == 'AWS::RDS::DBInstance'
]

rule check_db_instance_type when %rds !empty {
    %rds {
        Properties {
          DBInstanceClass in ['db.m6.large', 'db.m6.xlarge', 'db.m6.2xlarge']
        }
    }
}

rule check_public_accessibility when %rds !empty {
    %rds {
        Properties {
            PubliclyAccessible exists
        }
    }
}

rule check_storage_encryption when %rds !empty {
    %rds {
        Properties {
            StorageEncrypted exists
        }
    }
}
```

Finally let's examine the results:

```
PASS Expected Rule = check_db_instance_type, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_public_accessibility, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_storage_encryption, Status = SKIP, Got Status = SKIP
PASS Expected Rule = check_db_instance_type, Status = PASS, Got Status = PASS
PASS Expected Rule = check_public_accessibility, Status = PASS, Got Status = PASS
PASS Expected Rule = check_storage_encryption, Status = PASS, Got Status = PASS
```

All our tests are successful! As a final exercise let's add one more rule. Let's add:

* MasterUserPassword property must use either ssm or secretsmanager for the password

Below is the contents of both the rules and unit test file that checks for ssm or secrets manager.

unit test file **rds_compliance_test.yaml**:
```
- input:
    Resources: {}
  expectations:
    rules:
      check_db_instance_type: SKIP
      check_public_accessibility: SKIP
      check_storage_encryption: SKIP
- input:
    Resources:
      Rds00:
        Type: AWS::RDS::DBInstance
        Properties:
          DBInstanceClass: db.m6.large
          AllocatedStorage: 100
          Engine: oracle-se2
          EngineVersion: 19.0.0.0.ru-2020-04.rur-2020-04.r1
          MasterUsername: syscdk
          MasterUserPassword: x8204fsfxx
          PubliclyAccessible: true
          StorageType: gp2
          StorageEncrypted: true
        Metadata:
          aws:cdk:path: CdkRDSStack/Instance/Resource
  expectations:
    rules:
      check_db_instance_type: PASS
      check_public_accessibility: PASS
      check_storage_encryption: PASS
- input:
    Resources: {}
  expectations:
    rules:
      check_db_instance_type: SKIP
      check_public_accessibility: SKIP
      check_storage_encryption: SKIP
- input:
    Resources:
      Rds00:
        Type: AWS::RDS::DBInstance
        Properties:
          DBInstanceClass: db.m6.large
          AllocatedStorage: 100
          Engine: oracle-se2
          EngineVersion: 19.0.0.0.ru-2020-04.rur-2020-04.r1
          MasterUsername: syscdk
          MasterUserPassword: x8204fsfxx
          PubliclyAccessible: true
          StorageType: gp2
          StorageEncrypted: true
        Metadata:
          aws:cdk:path: CdkRDSStack/Instance/Resource
  expectations:
    rules:
      check_db_instance_type: PASS
      check_public_accessibility: PASS
      check_storage_encryption: PASS
      check_masterpassword_secretsmanager: FAIL
- input:
    Resources:
      Rds00:
        Type: AWS::RDS::DBInstance
        Properties:
          DBInstanceClass: db.m6.large
          AllocatedStorage: 100
          Engine: oracle-se2
          EngineVersion: 19.0.0.0.ru-2020-04.rur-2020-04.r1
          MasterUsername: syscdk
          MasterUserPassword: "{{resolve:secretsmanager:bbbb:SecretString:password::}}"
          PubliclyAccessible: true
          StorageType: gp2
          StorageEncrypted: true
        Metadata:
          aws:cdk:path: CdkRDSStack/Instance/Resource
  expectations:
    rules:
      check_db_instance_type: PASS
      check_public_accessibility: PASS
      check_storage_encryption: PASS
      check_masterpassword_secretsmanager: PASS
```

file **rds_compliance.guard**:

```
# add a global rds variable that we will use with all of our rules in this file
let rds = Resources.*[
    Type == 'AWS::RDS::DBInstance'
]

rule check_db_instance_type when %rds !empty {
    %rds {
        Properties {
          DBInstanceClass in ['db.m6.large', 'db.m6.xlarge', 'db.m6.2xlarge']
        }
    }
}

rule check_public_accessibility when %rds !empty {
    %rds {
        Properties {
            PubliclyAccessible exists
        }
    }
}

rule check_storage_encryption when %rds !empty {
    %rds {
        Properties {
            StorageEncrypted exists
        }
    }
}

rule check_masterpassword_secretsmanager when %rds !empty {
    %rds {
        Properties {
            MasterUserPassword is_string
            MasterUserPassword in [ /\{\{resolve:secretsmanager/, /\{\{resolve:ssm-secure/ ]
        }
    }
}
```
