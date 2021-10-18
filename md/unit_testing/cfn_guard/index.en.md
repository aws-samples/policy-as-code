---
title: "Cloudformation Guard"
weight: 21
---

**cfn-guard** is written in Rust. The unit tests will depend on the libraries **cfn-guard** uses for its unit test.

### Installing Rust and Cargo

[Rust](https://aws.amazon.com/blogs/opensource/why-aws-loves-rust-and-how-wed-like-to-help/) is programming language that had its 1.0 release in 2015. [Cargo](https://doc.rust-lang.org/cargo/) is the package manager for Rust, similiar to Pip for Python and Npm for Node.

```markdown
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

The installer will provide you with instructions. After installation source the environment into your shell as specified below.

```markdown
source $HOME/.cargo/env
```
For the latest Rust installation check [here](https://github.com/aws-cloudformation/cloudformation-guard#install-rust)

#### Install cfn-guard libraries
```
> cargo install cfn-guard
```

#### Validate Installation
```markdown
> cargo version
cargo 1.50.0 (f04e7fab7 2021-02-04)
```

```markdown
> rustc --version
rustc 1.50.0 (cb75ad5db 2021-02-10)
```


{{% notice note %}}
As Rust continues to get updates the version numbers may be different but this should be compatible regardless of the version number.
{{% /notice %}}

### Creating Cloudformation Guard Unit Test

Once you've installed Rust and Cargo, we need to create our project folder structure. Below is one opinion on doing this.

```
  securitygroup_rules
    ├── rules   <-- Folder where similiar grouped rules reside
    ├── target  <-- This gets created by cargo init. Not used. 
    └── tests   <-- Unit Tests
```

Run the commands below to create this structure and create a new Cargo package file (i.e. Cargo.toml)
```
> mkdir securitygroup_rules
> cd securitygroup_rules
> cargo init
> mkdir rules tests
> rm -rf src
```

Add **cfn-guard = "1.0.0"** dependency in the Cargo.toml file, it should look something like this when added
```
[package]
name = "securitygroup_rules"
version = "0.1.0"
authors = ["ec2-user"]
edition = "2018"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
cfn-guard = "1.0.0"
```

Run the cargo test, it should look something like this:
```
> cargo test
   Compiling securitygroup_rules v0.1.0 (/home/ec2-user/environment/securitygroup_rules)
    Finished test [unoptimized + debuginfo] target(s) in 1.19s
     Running target/debug/deps/securitygroup_rules-3fbad4c16dd97a66

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running target/debug/deps/securitygroup_tests-6694beb8d8b5f5b1

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Since we have not created unit tests we should see 0 tests run. Let's use one of the rules we created with the Security Group example. Create a file named securitygroup_tests.rs in the tests directory shown below:

```
// Tests
use cfn_guard;
use std::fs;

mod tests {
    use super::*;

    static RULESET: &str = "./rules/securitygroup.ruleset";

    #[test]
    fn allow_secure_port_only() {
        let template_contents = String::from(
            r#"
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
            "#);
        let rules_file_content = fs::read_to_string(RULESET)
            .expect("Couldn't read the file.")
        assert_ne!(
            cfn_guard::run_check(&template_contents, &rules_file_content, true).unwrap(),
            (vec![], 0)
        );
    }
}
```

Also, let's create a rules file but don't add any rules.

```
> touch ./rules/securitygroup.ruleset
```

Let's run the unit test again:
```
> cargo test
   Compiling securitygroup_rules v0.1.0 (/home/ec2-user/environment/securitygroup_rules)
    Finished test [unoptimized + debuginfo] target(s) in 1.62s
     Running target/debug/deps/securitygroup_tests-226ae47499572cce

running 1 test
test tests::allow_secure_port_only ... FAILED

failures:

---- tests::allow_secure_port_only stdout ----
thread 'tests::allow_secure_port_only' panicked at 'assertion failed: `(left != right)`
  left: `([], 0)`,
 right: `([], 0)`', tests/securitygroup_tests.rs:38:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::allow_secure_port_only

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass '--test securitygroup_tests'
```

This time the test fails but this is expected. We have are using the Rust function **assert_ne!**, which asserts true if the **cfn_guard::run_check** returns false or flags an issue with our cloudformation template. Since we have an empty rules file this returns true because the cloudformation template is not violating any rules. However, it should be in violation because it is using port 80 instead of 443. Let's add the rule we created in the Security Group example so that **cfn_guard::run_check** will flag an issue. Edit the **securitygroup.ruleset** and add **AWS::EC2::SecurityGroup SecurityGroupIngress.*.FromPort == 443**

```
AWS::EC2::SecurityGroup SecurityGroupIngress.*.FromPort == 443
```

Let's run the test again:
```
> cargo test
    Finished test [unoptimized + debuginfo] target(s) in 0.03s
     Running target/debug/deps/securitygroup_tests-226ae47499572cce

running 1 test
test tests::allow_secure_port_only ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.03s
```

This time our test passes. Because we are expecting a policy violation this unit test now passes. Congratulations you've written a successful unit test.