# pylint:disable=redefined-outer-name
import pytest
from botocore.exceptions import ClientError  # type: ignore

from cfn_sync.deleter import delete
from cfn_sync.stack import Stack

from .conftest import StubbedClient
from .stubs import (
    stub_delete_stack,
    stub_delete_stack_error,
    stub_describe_stack,
    stub_describe_stack_events,
)


def test_delete_success(fake_cloudformation_client: StubbedClient, stack: Stack):
    """Tests delete() successful cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    stub_delete_stack(fake_cloudformation_client.stub, "MyStack")
    delete(stack, False)


def test_delete_failure(fake_cloudformation_client: StubbedClient, stack: Stack):
    """Tests delete() failure cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE")
    stub_delete_stack_error(fake_cloudformation_client.stub, "Can not delete")
    with pytest.raises(ClientError):
        delete(stack, False)


def test_delete_wait_success(fake_cloudformation_client: StubbedClient, stack: Stack):
    """Tests delete(wait=True) successful cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_delete_stack(fake_cloudformation_client.stub, "MyStack")
    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "DELETE_COMPLETE", True
    )
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack", True)
    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "DELETE_COMPLETE", True
    )
    delete(stack, True)


def test_delete_wait_failure(fake_cloudformation_client: StubbedClient, stack: Stack):
    """Tests delete(wait=True) failure cases"""
    stub_describe_stack(fake_cloudformation_client.stub, "MyStack", "UPDATE_COMPLETE")
    stub_delete_stack(fake_cloudformation_client.stub, "MyStack")
    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "CREATE_COMPLETE", True
    )
    stub_describe_stack_events(fake_cloudformation_client.stub, "MyStack", True)
    stub_describe_stack(
        fake_cloudformation_client.stub, "MyStack", "DELETE_FAILED", True
    )
    with pytest.raises(Exception):
        delete(stack, True)
