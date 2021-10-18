---
title: "The Basics"
weight: 10
---

In this section we will focus on basic concepts needed to write cfn-guard rules.

### Clauses

Clauses are the foundational underpinning of Guard rules. Clauses are boolean statements which evaluate to a `true` (`PASS`)/ `false` (`FAIL`) and take the following format:

```
  <query> <operator> [query|value literal] 
```

You must specify a `query` and an `operator` in the clause section:

* `query` in its most simple form is a decimal dot (`.`) formatted expressions written to traverse hierarchical data. More information on this section of the clause can be found in the [Guard: Query and Filtering](QUERY_AND_FILTERING.md) document.

* `operator` can use *unary* or *binary* operators. Both of these operators will be discussed in-depth later in this document:

  * *Unary Operators:* `exists`, `empty`, `is_string`, `is_list`, `is_struct`, `not(!)`
  * *Binary Operators:* `==`, `!=`, `>`, `>=`, `<`, `<=`, `IN`

Let's try out a few clauses, first create a directory name **clauses_demo** and `cd` into it:


:::code{showCopyAction=true showLineNumbers=false language=shell}
mkdir clauses_demo; cd clauses_demo
:::

Next let's create sample cloudformation template that we can work with. Create a file name **rds_demo.yaml** with the following contents:


:::code{showCopyAction=true showLineNumbers=false}
Resources:
  Rds00:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.m5.large
      AllocatedStorage: 100
      Engine: mysql
      EngineVersion: 8.0.25
      MasterUsername: syscdk
      MasterUserPassword: x8204fsfxx
      StorageType: gp2
      StorageEncrypted: false
      Tags:
        - Key: BU
          Value: NumberCrunchers
:::


We'll make some assertions about the properties that are set to get us familiar with writing clauses. Let's validate that the tag for this resource is not empty. Create a file name **clause.guard** with the following content:

:::code{showCopyAction=true showLineNumbers=false language=shell}
Resources.*.Properties.Tags !empty
:::

One thing to note is the '*' would normally retrieve all the Resources in a Cloudformation template however for this exercise we only have a single resource. As we progress we'll discuss how to query and filter for specific resource types.

Let's run our validation to look at the results. Issue the following command:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clause.guard
:::

You'll get an output like this:

```
rds_demo.yaml Status = PASS
PASS rules
clauses.guard/default    PASS
---
```

Next let's limit the number of instances that you can deploy where the minimum is a large and the maximum is a xlarge db.m5 class type. Add the following clause to the file **clause.guard**:

:::code{showCopyAction=true showLineNumbers=false}
Resources.*.Properties.DBInstanceClass IN ['db.m5.large', 'db.m5.xlarge']
:::

Let's validate:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clause.guard
:::
```
rds_demo.yaml Status = PASS
PASS rules
clauses.guard/default    PASS
---
```

Here the **IN** operator will allow any of the listed instance types.

We'd like to check [AllocatedStorage](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-allocatedstorage) and provide a minimum and maximum. We could string together a series of operators like **>**, **>=**, **<=**, or **<** to do this, however let's use a range operator. Add the following clause to the file **clause.guard**:

:::code{showCopyAction=true showLineNumbers=false}
Resources.*.Properties.AllocatedStorage IN r[100, 1000]
:::

Running the validation:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clause.guard
:::
```
rds_demo.yaml Status = PASS
PASS rules
clauses.guard/default    PASS
---
```

You can also use **r(100, 1000)** where the '**()**' in a range means non-inclusive. So this range would not include 100 or 1000 but 101 and 999 would work.

Perhaps we might have another clause that restricts the [EngineVersion](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engineversion) we are allowed to use. Add the following clause to the file **clause.guard**:

:::code{showCopyAction=true showLineNumbers=false}
Resources.*.Properties.EngineVersion == /8.0.2[0-5]/
:::

This is an example of using a regex. This would restrict us to only [EngineVersion](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engineversion) 8.0.20 - 8.0.25. 

How would we check to make sure that our storage is encrypted? As a start we should see if the [StorageEncrypted](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-storageencrypted) property is set. Add the following clause to the file **clause.guard**:

:::code{showCopyAction=true showLineNumbers=false}
Resources.*.Properties.StorageEncrypted exists
:::

Running the validation again should yield something simliar to this:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clause.guard
:::
```
rds_demo.yaml Status = PASS
PASS rules
clauses.guard/default    PASS
---
```

However we should also check that the [StorageEncrypted](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance) is set to true. Add the following clause to the file **clause.guard**:

:::code{showCopyAction=true showLineNumbers=false}
Resources.*.Properties.StorageEncrypted == true
:::

> Be careful about when writing clauses dealing with booleans **true** and **false**. YAML/JSON assigns true and false with no quotes as boolean types where 'true' and 'false' with quotes will be recognized as a string type.

Let's run our validation:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clauses.guard
:::
```
rds_demo.yaml Status = FAIL
FAILED rules
clauses.guard/default    FAIL
---
`- File(, Status=FAIL)[Context=File(rules=1)]
   `- Rule(default, Status=FAIL)[Context=default]
      `- Check was not compliant as property value [Path=/Resources/Rds00/Properties/StorageEncrypted, Value=false] not equal to value [Path=, Value="/true/"].
```

We can add messages to better understand when validations fail. Replace the entire contents of our **clauses.guard** file with the contents below:

:::code{showCopyAction=true showLineNumbers=false}
Resources.*.Properties.Tags !empty
Resources.*.Properties.DBInstanceClass IN ['db.m5.large', 'db.m5.xlarge']
Resources.*.Properties.AllocatedStorage IN r[100, 1000]
Resources.*.Properties.EngineVersion == /8.0.2[0-5]/
Resources.*.Properties.StorageEncrypted == true
<< StorageEncrypted is set to false this needs to be set to true >>
:::

Let's run the validation:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clauses.guard
:::
```
rds_demo.yaml Status = FAIL
FAILED rules
clauses.guard/default    FAIL
---
`- File(, Status=FAIL)[Context=File(rules=1)]
   `- Rule(default, Status=FAIL)[Context=default]
      `- Check was not compliant as property value [Path=/Resources/Rds00/Properties/StorageEncrypted, Value=false] not equal to value [Path=, Value=true]. Message = [ StorageEncrypted is set to false this needs to be set to true ]
```

Notice that more context around the failed validation is given in Message field.

Now that we know why our clause is failing let's fix our cloudformation template by updating the value. You can just simply copy the contents below replace it in the **rds_demo.yaml** file ([StorageEncrypted](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance) is changed from false to true):

:::code{showCopyAction=true showLineNumbers=false}
Resources:
  Rds00:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.m5.large
      AllocatedStorage: 100
      Engine: mysql
      EngineVersion: 8.0.25
      MasterUsername: syscdk
      MasterUserPassword: x8204fsfxx
      StorageType: gp2
      StorageEncrypted: true
      Tags:
        - Key: BU
          Value: NumberCrunchers
:::

Running our validation again:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clauses.guard
:::
```
rds_demo.yaml Status = PASS
PASS rules
clauses.guard/default    PASS
---
```

We are back to PASS for our rule *clauses.guard/default*.

### Combining Clauses

Now that we have a complete picture of what constitutes a clause, let us learn to combine clauses. In Guard, each clause written on a new line is combined implicitly with the next clause using conjunction (boolean `and` logic):

```
# clause_A ^ clause_B ^ clause_C
clause_A
clause_B
clause_C
```

You can also combine a clause with the next clause using disjunction by specifying `or|OR` at the end of the first clause.

```
  <query> <operator> [query|value literal] [custom message] [or|OR]
```

Disjunctions are evaluated first followed by conjunctions, and hence Guard rules can be defined as a conjunction of disjunction of clauses that evaluate to a `true` (`PASS`) / `false` (`FAIL`). This can be best explained with a few examples:

```
# (clause_E v clause_F) ^ clause_G
clause_E OR clause_F
clause_G

# (clause_H v clause_I) ^ (clause_J v clause_K)
clause_H OR
clause_I
clause_J OR
clause_K

# (clause_L v clause_M v clause_N) ^ clause_O
clause_L OR
clause_M OR
clause_N 
clause_O
```

This is similar to the [Conjunctive Normal Form (CNF)](https://en.wikipedia.org/wiki/Conjunctive_normal_form).

```
Resources.*.Properties.Tags !empty
Resources.*.Properties.DBInstanceClass IN ['db.m5.large', 'db.m5.xlarge']
Resources.*.Properties.AllocatedStorage IN r[100, 1000]
Resources.*.Properties.EngineVersion == /8.0.2[0-5]/
Resources.*.Properties.StorageEncrypted == true
<< StorageEncrypted is set to false this needs to be set to true >>
```

All clauses above are combined using conjunction. As you can see, there is repetition of part of the query expression in every clause. You can improve composability and remove verbosity and repetition from a set of related clauses with the same initial query path using a query block.

### Query blocks

Like all good coders we need to simplify our rules for maintainability. Let's use query blocks to simpify this a bit. Update the entire contents of your **clauses.guard** file with the contents below:

:::code{showCopyAction=true showLineNumbers=false}
Resources.*.Properties {
    Tags !empty
    DBInstanceClass IN ['db.m5.large', 'db.m5.xlarge']
    AllocatedStorage IN r[100, 1000]
    EngineVersion == /8.0.2[0-5]/
    StorageEncrypted == true
        << StorageEncrypted is set to false this needs to be set to true >>
}
:::

As always we should validate our template to make sure the rules file is syntactically correct:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clauses.guard
:::
```
rds_demo.yaml Status = PASS
PASS rules
clauses.guard/default    PASS
---
```

### When blocks - When condition for conditional evaluation

Up to this point we've been specifiying **Resources.\*** which grab all the resource in a cloudformation template. This has been working for us but only because we have a single resource in our cloudformation template. We need to select only the resources we are interested in validating. Otherwise, we run the risk of a FAIL validating a resource that our clauses don't apply to. Let's fix that now. Replace the entire contents of the **clauses.guard** file with:

:::code{showCopyAction=true showLineNumbers=false}
when Resources.*.Type == 'AWS::RDS::DBInstance' {
    Resources.*.Properties {
        Tags !empty
        DBInstanceClass IN ['db.m5.large', 'db.m5.xlarge']
        AllocatedStorage IN r[100, 1000]
        EngineVersion == /8.0.2[0-5]/
        StorageEncrypted == true
            << StorageEncrypted is set to false this needs to be set to true >>
    }
}
:::

The **when** statement will ensure that we only check resources of type 'AWS::RDS::DBInstance'. Once updated let's run our validation:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clauses.guard
:::
```
rds_demo.yaml Status = PASS
PASS rules
clauses.guard/default    PASS
---
```

### Named rule blocks
Named rule blocks allow for re-usability, improved composition and remove verbosity and repetition. They take the following form:

```
  rule <rule name> [when <condition>] {
      Guard_rule_1
      Guard_rule_2
      ...
  }
```

* The `rule` keyword designates the start of a named rule block.

* `rule name` can be any string that is human-readable and ideally should uniquely identify a named rule block. It can be thought of as a label to the set of Guard rules it encapsulates where Guard rules is an umbrella term for clauses, query blocks, when blocks and named rule blocks. The `rule name` can be used to refer to the evaluation result of the set of Guard rules it encapsulates, this is what makes named rule blocks re-usable. It also helps provide context in the validate (provide links) and test (provide links) command output as to what exactly failed. The `rule name` is displayed along with it block’s evaluation status - `PASS`, `FAIL`, or `SKIP`, in the evaluation output of the rules file:

```
# Sample output of an evaluation where check1, check2, and check3 are rule names.
_Summary__ __Report_ Overall File Status = **FAIL**
**PASS/****SKIP** **rules**
check1 **SKIP**
check2 **PASS**
**FAILED rules**
check3 **FAIL**
```

* Named rule blocks can also be evaluated conditionally by specifying the `when` keyword followed with a `condition` after the `rule name`.

The name of our rule, *clauses.guard/default*, is the default because we have not created any named rules so let's create one, update the entire contents of your **clauses.guard** file with the contents below:

:::code{showCopyAction=true showLineNumbers=false}
rule allowed_rds_properties when Resources.*.Type == 'AWS::RDS::DBInstance' {
    Resources.*.Properties {
        Tags !empty
        DBInstanceClass IN ['db.m5.large', 'db.m5.xlarge']
        AllocatedStorage IN r[100, 1000]
        EngineVersion == /8.0.2[0-5]/
        StorageEncrypted == true
            << StorageEncrypted is set to false this needs to be set to true >>
    }
}
:::

Again, let's validate our template:

:::code{showCopyAction=true showLineNumbers=false language=shell}
cfn-guard validate -d rds_demo.yaml -r clauses.guard
:::
```
rds_demo.yaml Status = PASS
PASS rules
clauses.guard/allowed_rds_properties    PASS
```

Congratulations you've written your first cfn-guard rule!