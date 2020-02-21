# pylint:disable=redefined-outer-name
import pytest
from botocore.exceptions import ClientError  # type: ignore

from cfn_deploy import cloudformation
from .stubs import (
    stub_describe_stack,
    stub_describe_stack_error,
    stub_create_stack,
    stub_create_stack_error,
    stub_update_stack,
    stub_update_stack_error,
    stub_describe_stack_events,
)
from .conftest import StubbedClient


@pytest.fixture
def stack(fake_cloudformation_client: StubbedClient) -> cloudformation.Stack:
    """Create a Stack object"""
    return cloudformation.Stack(fake_cloudformation_client.client, "MyStack")


def test_status(fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack):
    """Tests Stack.status"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    assert stack.status == "UPDATE_COMPLETE"

    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "UPDATE_ROLLBACK_COMPLETE"
    )
    assert stack.status == "UPDATE_ROLLBACK_COMPLETE"


def test_exists(fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack):
    """Tests Stack.exists"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    assert stack.exists

    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    assert stack.exists

    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "CREATE_IN_PROGRESS"
    )
    assert stack.exists


def test_exists_not_exists(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.exists with an error message"""
    stub_describe_stack_error(fake_cloudformation_client.stub)
    assert not stack.exists


def test_exists_different_error(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.exists with a non-stack does not exist message"""
    stub_describe_stack_error(
        fake_cloudformation_client.stub, "A general error occurred"
    )

    with pytest.raises(ClientError):
        _ = stack.exists


def test_deploy_update_success(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.deploy() update successful cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        "https://s3.amazonaws.com/my-path/template.yml",
        [{"ParameterKey": "Hello", "ParameterValue": "You"}],
        [{"Key": "MyTag", "Value": "TagValue"}],
    )
    stack.deploy(
        "https://s3.amazonaws.com/my-path/template.yml",
        {"Hello": "You"},
        {"MyTag": "TagValue"},
        False,
    )


def test_deploy_update_errors(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.deploy() update failure cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack_error(fake_cloudformation_client.stub)
    stack.deploy(
        "https://s3.amazonaws.com/my-path/template.yml",
        {"Hello": "You"},
        {"MyTag": "TagValue"},
        False,
    )

    # Test some other kind of error
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack_error(fake_cloudformation_client.stub, "Template invalid")
    with pytest.raises(ClientError):
        stack.deploy(
            "https://s3.amazonaws.com/my-path/template.yml",
            {"Hello": "You"},
            {"MyTag": "TagValue"},
            False,
        )


def test_deploy_create_success(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.deploy() create successful cases"""
    stub_describe_stack_error(
        fake_cloudformation_client.stub
    )  # to trigger create workflow
    stub_create_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        "https://s3.amazonaws.com/my-path/template.yml",
        [{"ParameterKey": "Hello", "ParameterValue": "You"}],
        [{"Key": "MyTag", "Value": "TagValue"}],
    )
    stack.deploy(
        "https://s3.amazonaws.com/my-path/template.yml",
        {"Hello": "You"},
        {"MyTag": "TagValue"},
        False,
    )


def test_deploy_create_errors(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.deploy() update failure cases"""
    stub_describe_stack_error(
        fake_cloudformation_client.stub
    )  # to trigger create workflow
    stub_create_stack_error(fake_cloudformation_client.stub, "Template invalid")
    with pytest.raises(ClientError):
        stack.deploy(
            "https://s3.amazonaws.com/my-path/template.yml",
            {"Hello": "You"},
            {"MyTag": "TagValue"},
            False,
        )


def test_deploy_wait_success(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.deploy(wait=True) successful cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        "https://s3.amazonaws.com/my-path/template.yml",
        [{"ParameterKey": "Hello", "ParameterValue": "You"}],
        [{"Key": "MyTag", "Value": "TagValue"}],
    )
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    stack.deploy(
        "https://s3.amazonaws.com/my-path/template.yml",
        {"Hello": "You"},
        {"MyTag": "TagValue"},
        True,
    )


def test_deploy_wait_failure(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.deploy(wait=True) failure cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        "https://s3.amazonaws.com/my-path/template.yml",
        [{"ParameterKey": "Hello", "ParameterValue": "You"}],
        [{"Key": "MyTag", "Value": "TagValue"}],
    )
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "ROLLBACK_COMPLETE")
    with pytest.raises(Exception):
        stack.deploy(
            "https://s3.amazonaws.com/my-path/template.yml",
            {"Hello": "You"},
            {"MyTag": "TagValue"},
            True,
        )


def test_wait_success(
    fake_cloudformation_client: StubbedClient, stack: cloudformation.Stack
):
    """Tests Stack.wait() success cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
    stack.wait()

    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "CREATE_IN_PROGRESS"
    )
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    stack.wait()

    print("done")
