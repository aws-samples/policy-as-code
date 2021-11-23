---
title: "Installing cfn-guard"
weight: 10
---
This section provides instruction on installation of cfn-guard 2.0

1. Install [Rust](https://www.rust-lang.org/tools/install)
    :::code{showCopyAction=true showLineNumbers=false}
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh;source ~/.bash_profile
    :::
    Choose "1) Proceed with installation (default)" or hit enter.
1. cfn-guard - [Installing cfn-guard](https://github.com/aws-cloudformation/cloudformation-guard#installation)
    ```
    git clone https://github.com/dchakrav-github/cloudformation-guard
    cd cloudformation-guard
    git switch parameterized-rules
    cargo build --release
    mkdir -p ~/bin;cp ./target/release/cfn-guard ~/bin
    cfn-guard --version
    ```