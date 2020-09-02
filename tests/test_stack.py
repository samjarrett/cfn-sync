# pylint:disable=redefined-outer-name
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError  # type: ignore

from cfn_sync.stack import Stack, parameter_dict_to_list, tag_dict_to_list

from .conftest import StubbedClient
from .stubs import (
    stub_describe_stack,
    stub_describe_stack_error,
    stub_describe_stack_events,
)


def test_parameter_dict_to_list():
    """Tests parameter_dict_to_list()"""
    parameter_dict = {
        "ParamOne": "value1",
        "ParamTwo": "value2",
    }
    parameter_list = [
        {"ParameterKey": "ParamOne", "ParameterValue": "value1"},
        {"ParameterKey": "ParamTwo", "ParameterValue": "value2"},
    ]
    assert parameter_dict_to_list(parameter_dict) == parameter_list

    parameter_dict = {
        "ParamThree": "value3",
        "ParamTwo": "value2",
    }
    parameter_list = [
        {"ParameterKey": "ParamThree", "ParameterValue": "value3"},
        {"ParameterKey": "ParamTwo", "ParameterValue": "value2"},
    ]
    assert parameter_dict_to_list(parameter_dict) == parameter_list


def test_tag_dict_to_list():
    """Tests tag_dict_to_list()"""
    tag_dict = {
        "ParamOne": "value1",
        "ParamTwo": "value2",
    }
    tag_list = [
        {"Key": "ParamOne", "Value": "value1"},
        {"Key": "ParamTwo", "Value": "value2"},
    ]
    assert tag_dict_to_list(tag_dict) == tag_list

    tag_dict = {
        "ParamThree": "value3",
        "ParamTwo": "value2",
    }
    tag_list = [
        {"Key": "ParamThree", "Value": "value3"},
        {"Key": "ParamTwo", "Value": "value2"},
    ]
    assert tag_dict_to_list(tag_dict) == tag_list


def test_status(fake_cloudformation_client: StubbedClient, stack: Stack):
    """Tests Stack.status"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    assert stack.status == "UPDATE_COMPLETE"

    # Subsequent calls use the ID
    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "UPDATE_ROLLBACK_COMPLETE"
    )
    assert stack.status == "UPDATE_ROLLBACK_COMPLETE"


def test_parameters(fake_cloudformation_client: StubbedClient, stack: Stack):
    """Tests Stack.parameters"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    assert stack.parameters == {}

    stub_describe_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        "UPDATE_ROLLBACK_COMPLETE",
        parameters={"MyParam": "MyValue"},
    )
    assert stack.parameters == {"MyParam": "MyValue"}


def test_tags(fake_cloudformation_client: StubbedClient, stack: Stack):
    """Tests Stack.tags"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    assert stack.tags == {}

    stub_describe_stack(
        fake_cloudformation_client.stub,
        "MyStack",
        "UPDATE_ROLLBACK_COMPLETE",
        tags={"MyTag": "MyValue"},
    )
    assert stack.tags == {"MyTag": "MyValue"}


def test_exists(fake_cloudformation_client: StubbedClient, stack: Stack):
    """Tests Stack.exists"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    assert stack.exists

    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    assert stack.exists

    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "CREATE_IN_PROGRESS"
    )
    assert stack.exists


def test_exists_not_exists(fake_cloudformation_client: StubbedClient, stack: Stack):
    """Tests Stack.exists with an error message"""
    stub_describe_stack_error(fake_cloudformation_client.stub)
    assert not stack.exists


def test_exists_different_error(
    fake_cloudformation_client: StubbedClient, stack: Stack
):
    """Tests Stack.exists with a non-stack does not exist message"""
    stub_describe_stack_error(
        fake_cloudformation_client.stub, "A general error occurred"
    )

    with pytest.raises(ClientError):
        _ = stack.exists


@patch("time.sleep")
def test_wait_delay(
    patched_sleep: MagicMock,
    fake_cloudformation_client: StubbedClient,
    stack: Stack,
):
    """Tests Stack.wait_delay and Stack.wait()"""
    # test default is 5 sec
    def perform_wait(stack: Stack, fake_cloudformation_client: StubbedClient):
        stub_describe_stack(
            fake_cloudformation_client.stub, "MyStack", "CREATE_IN_PROGRESS"
        )
        stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
        stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
        stub_describe_stack(
            fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE"
        )
        stack.wait()

    perform_wait(stack, fake_cloudformation_client)
    patched_sleep.assert_called_once_with(5)

    patched_sleep.reset_mock()
    stack.wait_delay = 30
    perform_wait(stack, fake_cloudformation_client)
    patched_sleep.assert_called_once_with(30)

    patched_sleep.reset_mock()
    stack.wait_delay = 300
    perform_wait(stack, fake_cloudformation_client)
    patched_sleep.assert_called_once_with(300)


@patch("time.sleep")
def test_wait_success(
    patched_sleep: MagicMock,
    fake_cloudformation_client: StubbedClient,
    stack: Stack,
):
    """Tests Stack.wait() success cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
    stack.wait()
    patched_sleep.assert_not_called()

    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "CREATE_IN_PROGRESS"
    )
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack")
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    stack.wait()
    patched_sleep.assert_called_once()
