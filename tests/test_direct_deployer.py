# pylint:disable=redefined-outer-name
import pytest
from botocore.exceptions import ClientError  # type: ignore

from cfn_sync.direct_deployer import deploy
from cfn_sync.stack import Stack

from .conftest import StubbedClient
from .stubs import (
    stub_create_stack,
    stub_create_stack_error,
    stub_describe_stack,
    stub_describe_stack_error,
    stub_describe_stack_events,
    stub_update_stack,
    stub_update_stack_error,
)


def test_deploy_update_success(
    fake_cloudformation_client: StubbedClient,
    stack: Stack,
    demo_template: str,
):
    """Tests deploy() update successful cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        demo_template,
        [{"ParameterKey": "Hello", "ParameterValue": "You"}],
        [{"Key": "MyTag", "Value": "TagValue"}],
    )
    deploy(stack, demo_template, {"Hello": "You"}, {"MyTag": "TagValue"}, False)


def test_deploy_update_capabilities_success(
    fake_cloudformation_client: StubbedClient,
    stack: Stack,
    demo_template: str,
):
    """Tests deploy() update successful cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        demo_template,
        [{"ParameterKey": "Hello", "ParameterValue": "You"}],
        [{"Key": "MyTag", "Value": "TagValue"}],
        ["CAPABILITY_IAM"],
    )
    stack.set_capabilities(["CAPABILITY_IAM"])
    deploy(stack, demo_template, {"Hello": "You"}, {"MyTag": "TagValue"}, False)


def test_deploy_update_failure(
    fake_cloudformation_client: StubbedClient,
    stack: Stack,
    demo_template: str,
):
    """Tests deploy() update failure cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack_error(fake_cloudformation_client.stub)
    deploy(stack, demo_template, {"Hello": "You"}, {"MyTag": "TagValue"}, False)

    # Test some other kind of error
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack_error(fake_cloudformation_client.stub, "Template invalid")
    with pytest.raises(ClientError):
        deploy(stack, demo_template, {"Hello": "You"}, {"MyTag": "TagValue"}, False)


def test_deploy_create_success(
    fake_cloudformation_client: StubbedClient,
    stack: Stack,
    demo_template: str,
):
    """Tests deploy() create successful cases"""
    stub_describe_stack_error(
        fake_cloudformation_client.stub
    )  # to trigger create workflow
    stub_create_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        demo_template,
        [{"ParameterKey": "Hello", "ParameterValue": "You"}],
        [{"Key": "MyTag", "Value": "TagValue"}],
    )
    deploy(
        stack,
        demo_template,
        {"Hello": "You"},
        {"MyTag": "TagValue"},
        False,
    )


def test_deploy_create_failure(
    fake_cloudformation_client: StubbedClient,
    stack: Stack,
    demo_template: str,
):
    """Tests deploy() update failure cases"""
    stub_describe_stack_error(
        fake_cloudformation_client.stub
    )  # to trigger create workflow
    stub_create_stack_error(fake_cloudformation_client.stub, "Template invalid")
    with pytest.raises(ClientError):
        deploy(stack, demo_template, {"Hello": "You"}, {"MyTag": "TagValue"}, False)


def test_deploy_wait_success(
    fake_cloudformation_client: StubbedClient,
    stack: Stack,
    demo_template: str,
):
    """Tests deploy(wait=True) successful cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        demo_template,
        [{"ParameterKey": "Hello", "ParameterValue": "You"}],
        [{"Key": "MyTag", "Value": "TagValue"}],
    )
    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE", True
    )
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack", True)
    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE", True
    )
    deploy(stack, demo_template, {"Hello": "You"}, {"MyTag": "TagValue"}, True)


def test_deploy_wait_failure(
    fake_cloudformation_client: StubbedClient,
    stack: Stack,
    demo_template: str,
):
    """Tests deploy(wait=True) failure cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_update_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        demo_template,
        [{"ParameterKey": "Hello", "ParameterValue": "You"}],
        [{"Key": "MyTag", "Value": "TagValue"}],
    )
    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE", True
    )
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack", True)
    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "ROLLBACK_COMPLETE", True
    )
    with pytest.raises(Exception):
        deploy(stack, demo_template, {"Hello": "You"}, {"MyTag": "TagValue"}, True)
