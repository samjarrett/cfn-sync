import os
from collections import namedtuple

import pytest
import boto3
from botocore.stub import Stubber

# prevent boto from looking for IAM creds via metadata while running tests
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"


StubbedClient = namedtuple("StubbedClient", ["stub", "client"])


@pytest.yield_fixture
def fake_cloudformation_client() -> StubbedClient:
    """Creates a stubbed boto3 CloudFormation client"""
    cloudformation = boto3.client("cloudformation")
    with Stubber(cloudformation) as stubbed_client:
        yield StubbedClient(stubbed_client, cloudformation)
        stubbed_client.assert_no_pending_responses()


@pytest.yield_fixture
def demo_template():
    """Returns the contents of demo.yml"""
    dirname = os.path.dirname(__file__)
    with open(f"{dirname}/demo.yml", "r") as template_file:
        yield template_file.read()
