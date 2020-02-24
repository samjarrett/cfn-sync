from typing import Dict, List, Optional
from datetime import datetime
import uuid

from botocore.stub import ANY


def generate_stack_id(stack_name: str) -> str:
    """Generate a stack ID from the stack name"""
    return (
        f"arn:aws:cloudformation:ap-southeast-2:123456789012:stack/{stack_name}/"
        "bd6129c0-de8c-11e9-9c70-0ac26335768c"
    )


def stub_get_parameter_value(
    stubber, name: str, value: str, version: int = 1, param_type: str = "String",
):
    """Stubs SSM get_parameter_value responses"""
    response = {
        "Parameter": {
            "Name": name,
            "Type": param_type,
            "Value": value,
            "Version": version,
            "LastModifiedDate": datetime(2020, 1, 1),
            "ARN": f"arn:aws:ssm:ap-southeast-2:305295870059:parameter/{name.strip('/')}",
        }
    }
    stubber.add_response(
        "get_parameter",
        response,
        expected_params={"Name": name, "WithDecryption": True},
    )


def stub_get_parameter_unset(stubber, name: str):
    """Stubs SSM get_parameter_value responses where the parameter is unset"""
    stubber.add_client_error(
        "get_parameter",
        "ParameterNotFound",
        "Parameter was not found",
        400,
        expected_params={"Name": name, "WithDecryption": True},
    )


def stub_put_parameter_value(
    stubber, name: str, description: str, value: str, version: int = 1
):
    """Stubs SSM put_parameter_value responses"""
    response = {
        "Version": version,
    }
    stubber.add_response(
        "put_parameter",
        response,
        expected_params={
            "Name": name,
            "Description": description,
            "Value": value,
            "Type": "SecureString",
            "Overwrite": True,
        },
    )


def stub_add_tags_to_resource(stubber, name: str, tags: List[Dict]):
    """Stubs SSM add_tags_to_resource responses"""
    stubber.add_response(
        "add_tags_to_resource",
        {},
        expected_params={
            "ResourceType": "Parameter",
            "ResourceId": name,
            "Tags": tags,
        },
    )


def stub_describe_stack(
    stubber, stack_name: str, status: str, use_stack_id: bool = False
):
    """Stubs CloudFormation describe_stacks responses"""
    stack_id = generate_stack_id(stack_name)
    response = {
        "Stacks": [
            {
                "StackName": stack_name,
                "StackId": stack_id,
                "StackStatus": status,
                "CreationTime": datetime(2020, 1, 1),
            }
        ]
    }

    stack_name_param = stack_name
    if use_stack_id:
        stack_name_param = stack_id

    stubber.add_response(
        "describe_stacks", response, expected_params={"StackName": stack_name_param},
    )


def stub_describe_stack_error(
    stubber, error_message: str = "Stack with id abcxyz does not exist"
):
    """Stubs CloudFormation describe_stacks responses when an error occurs"""

    stubber.add_client_error(
        "describe_stacks",
        "ClientError",
        error_message,
        400,
        expected_params={"StackName": ANY},
    )


def stub_update_stack(
    stubber,
    stack_name: str,
    template_body: str,
    parameters: List[Dict],
    tags: List[Dict],
    capabilities: Optional[List] = None,
):  # pylint: disable=too-many-arguments
    """Stubs CloudFormation update_stack responses"""
    response = {"StackId": generate_stack_id(stack_name)}
    stubber.add_response(
        "update_stack",
        response,
        expected_params={
            "StackName": stack_name,
            "TemplateBody": template_body,
            "Parameters": parameters,
            "Tags": tags,
            "Capabilities": capabilities or [],
        },
    )


def stub_update_stack_error(
    stubber, error_message: str = "No updates are to be performed."
):
    """Stubs CloudFormation update_stack responses when an error occurs"""
    stubber.add_client_error(
        "update_stack",
        "ClientError",
        error_message,
        400,
        expected_params={
            "StackName": ANY,
            "Parameters": ANY,
            "TemplateBody": ANY,
            "Tags": ANY,
            "Capabilities": ANY,
        },
    )


def stub_create_stack(
    stubber,
    stack_name: str,
    template_body: str,
    parameters: List[Dict],
    tags: List[Dict],
    capabilities: Optional[List] = None,
):  # pylint: disable=too-many-arguments
    """Stubs CloudFormation create_stack responses"""
    response = {"StackId": generate_stack_id(stack_name)}
    stubber.add_response(
        "create_stack",
        response,
        expected_params={
            "StackName": stack_name,
            "TemplateBody": template_body,
            "Parameters": parameters,
            "Tags": tags,
            "Capabilities": capabilities or [],
        },
    )


def stub_create_stack_error(stubber, error_message: str):
    """Stubs CloudFormation update_stack responses when an error occurs"""
    stubber.add_client_error(
        "create_stack",
        "ClientError",
        error_message,
        400,
        expected_params={
            "StackName": ANY,
            "Parameters": ANY,
            "TemplateBody": ANY,
            "Tags": ANY,
            "Capabilities": ANY,
        },
    )


def stub_delete_stack(stubber, stack_name: str):
    """Stubs CloudFormation delete_stack responses"""
    stubber.add_response(
        "delete_stack", {}, expected_params={"StackName": stack_name},
    )


def stub_delete_stack_error(stubber, error_message: str):
    """Stubs CloudFormation delete_stack responses when an error occurs"""
    stubber.add_client_error(
        "delete_stack",
        "ClientError",
        error_message,
        400,
        expected_params={"StackName": ANY},
    )


def stub_describe_stack_events(stubber, stack_name: str, use_stack_id: bool = False):
    """Stubs CloudFormation describe_stack_events responses"""
    stack_id = generate_stack_id(stack_name)

    response = {
        "StackEvents": [
            {
                "StackId": stack_id,
                "EventId": str(uuid.uuid4()),
                "StackName": stack_name,
                "LogicalResourceId": "Something",
                "Timestamp": datetime(2020, 1, 1),
                "ResourceStatus": "CREATE_IN_PROGRESS",
                "ResourceStatusReason": "Resource creation initiated",
            },
            {
                "StackId": stack_id,
                "EventId": str(uuid.uuid4()),
                "StackName": stack_name,
                "LogicalResourceId": "Something",
                "Timestamp": datetime(2020, 1, 1),
                "ResourceStatus": "CREATE_COMPLETE",
            },
        ]
    }

    stack_name_param = stack_name
    if use_stack_id:
        stack_name_param = stack_id

    stubber.add_response(
        "describe_stack_events",
        response,
        expected_params={"StackName": stack_name_param},
    )
