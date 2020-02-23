# CFN-Sync

Deploy CloudFormation stacks synchronously using syntax similar to `aws cloudformation deploy`, and watch the events
scroll until the create or update completes.

## Installation

Install using pip/pypi:

```bash
pip install cfn-sync
```

## Usage

Deploying (creating or updating) a stack:

```bash
cfn-sync deploy --stack-name <STACK NAME> [--parameter-overrides <Key=Value> [<Key=Value>...]] [--tags <Key=Value> [<Key=Value>...]]
```

Deleting a stack:

```bash
cfn-sync delete --stack-name <STACK NAME>
```
