import logging
from typing import Callable, Dict

from botocore.exceptions import ClientError  # type: ignore

from .stack import (
    SUCCESSFUL_STACK_STATUSES,
    Stack,
    parameter_dict_to_list,
    tag_dict_to_list,
)

logger = logging.getLogger(__name__)


def deploy(
    stack: Stack,
    template_body: str,
    parameters: Dict,
    tags: Dict,
    wait: bool = True,
):
    """Performs a create/update against the stack and optionally waits for it to stabilise"""
    try:
        if stack.exists:
            logger.debug("Stack exists - setting method to update_stack")
            method: Callable = stack.cloudformation.update_stack
        else:
            logger.debug("Stack does not exist - setting method to create_stack")
            method = stack.cloudformation.create_stack

        response = method(
            StackName=stack.name,
            TemplateBody=template_body,
            Parameters=parameter_dict_to_list(parameters),
            Tags=tag_dict_to_list(tags),
            Capabilities=stack.capabilities or [],
        )
        stack.id = response["StackId"]
    except ClientError as client_error:
        if (
            client_error.response["Error"]["Message"]
            == "No updates are to be performed."
        ):
            logger.info(f"No changes. Stack {stack.name} not updated")
            return

        raise client_error

    if wait:
        stack.wait()

        stack_status = stack.status

        if stack_status not in SUCCESSFUL_STACK_STATUSES:
            raise Exception(
                f"Stack did not deploy successfully: {stack.name} is in {stack_status} status"
            )
