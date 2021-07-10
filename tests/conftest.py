# pylint:disable=redefined-outer-name
import os
from collections import namedtuple

import boto3
import pytest
from botocore.stub import Stubber

from cfn_sync.stack import Stack

# prevent boto from looking for IAM creds via metadata while running tests
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


StubbedClient = namedtuple("StubbedClient", ["stub", "client"])


@pytest.fixture
def fake_cloudformation_client() -> StubbedClient:
    """Creates a stubbed boto3 CloudFormation client"""
    cloudformation = boto3.client("cloudformation")
    with Stubber(cloudformation) as stubbed_client:
        yield StubbedClient(stubbed_client, cloudformation)
        stubbed_client.assert_no_pending_responses()


@pytest.fixture
def demo_template():
    """Returns the contents of demo.yml"""
    dirname = os.path.dirname(__file__)
    with open(f"{dirname}/demo.yml", "r") as template_file:
        yield template_file.read()


@pytest.fixture
def stack(fake_cloudformation_client: StubbedClient) -> Stack:
    """Create a Stack object"""
    return Stack(fake_cloudformation_client.client, "MyStack")
