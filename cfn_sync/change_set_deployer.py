import logging
from typing import Dict
import uuid

from botocore.exceptions import ClientError, WaiterError  # type: ignore

from .stack import (
    SUCCESSFUL_STACK_STATUSES,
    Stack,
    parameter_dict_to_list,
    tag_dict_to_list,
)

CHANGE_SET_CREATE = "CREATE"
CHANGE_SET_UPDATE = "UPDATE"

NO_CHANGE_ERROR = (
    "The submitted information didn't contain changes. "
    "Submit different information to create a change set."
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
    change_set_name = f"cfn-sync-{uuid.uuid4()}"
    change_set_type = CHANGE_SET_CREATE
    if stack.exists:
        logger.debug("Stack exists - setting ChangeSetType to UPDATE")
        change_set_type = CHANGE_SET_UPDATE

    logger.info(f"Creating {change_set_type.lower()} change set: {change_set_name}")
    response = stack.cloudformation.create_change_set(
        StackName=stack.name,
        ChangeSetName=change_set_name,
        ChangeSetType=change_set_type,  # type: ignore
        TemplateBody=template_body,
        Parameters=parameter_dict_to_list(parameters),
        Tags=tag_dict_to_list(tags),
        Capabilities=stack.capabilities or [],
    )
    stack.id = response["StackId"]
    change_set_id = response["Id"]

    try:
        logger.info("Waiting for change set to be created")
        waiter = stack.cloudformation.get_waiter("change_set_create_complete")
        waiter.wait(ChangeSetName=change_set_id, WaiterConfig={"Delay": 10})
    except WaiterError as waiter_error:
        if waiter_error.last_response["StatusReason"] == NO_CHANGE_ERROR:
            logger.info(f"No changes. Stack {stack.name} not updated")
            stack.cloudformation.delete_change_set(ChangeSetName=change_set_id)
            return

        raise

    stack.cloudformation.execute_change_set(
        ChangeSetName=change_set_id, ClientRequestToken=change_set_name
    )

    if wait:
        stack.wait()

        stack_status = stack.status

        if stack_status not in SUCCESSFUL_STACK_STATUSES:
            raise Exception(
                f"Stack did not deploy successfully: {stack.name} is in {stack_status} status"
            )
