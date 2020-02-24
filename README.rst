CFN-Sync
========

Deploy CloudFormation stacks synchronously using syntax similar to `aws cloudformation deploy`, and watch the events
scroll until the create or update completes.

Installation
------------

Install using pip/pypi:

::

    pip install cfn-sync


Usage
-----

Deploying (creating or updating) a stack:

::

    cfn-sync deploy \
      --stack-name <STACK_NAME> \
      --template-file <FILE_PATH> \
      [--parameter-overrides <KEY=VALUE> [<KEY=VALUE>...]] \
      [--tags <KEY=VALUE> [<KEY=VALUE>...]] \
      [--capabilities <VALUE> [<VALUE>...]]


Deleting a stack:

::

    cfn-sync delete --stack-name <STACK_NAME>
