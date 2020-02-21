import logging
import time
from typing import Dict, Optional

from botocore.exceptions import ClientError  # type: ignore


IN_PROGRESS_STACK_STATUSES = [
    "CREATE_IN_PROGRESS",
    "ROLLBACK_IN_PROGRESS",
    "DELETE_IN_PROGRESS",
    "UPDATE_IN_PROGRESS",
    "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
    "UPDATE_ROLLBACK_IN_PROGRESS",
    "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
    "REVIEW_IN_PROGRESS",
    "IMPORT_IN_PROGRESS",
    "IMPORT_ROLLBACK_IN_PROGRESS",
]

SUCCESSFUL_STACK_STATUSES = [
    "CREATE_COMPLETE",
    "UPDATE_COMPLETE",
    "IMPORT_COMPLETE",
]

logger = logging.getLogger(__name__)


def log_event(
    logical_resource_id: str, resource_status: str, status_reason: Optional[str] = None
):
    """Formats and logs a CloudFormation stack event"""
    if status_reason:
        return logger.info(
            "{} - {} - {}", logical_resource_id, resource_status, status_reason
        )

    return logger.info("{} - {}", logical_resource_id, resource_status)


class Stack:
    """Class that holds information about a CloudFormation stack, and can perform updates to it"""

    name: str

    def __init__(
        self, cloudformation, name: str,
    ):
        self.cloudformation = cloudformation
        self.name = name

    @property
    def status(self) -> str:
        """Retrieves the stack's current status"""
        return self.__describe()["StackStatus"]

    @property
    def exists(self) -> bool:
        """Checks if the stack currently exists or not"""
        try:
            self.__describe()

            return True
        except ClientError as exception:
            exception_message = str(exception)

            if "does not exist" in exception_message:
                return False

            raise exception

    def deploy(
        self, template_url: str, parameters: Dict, tags: Dict, wait: bool = True,
    ):
        """Performs a create/update against the stack and optionally waits for it to stabilise"""
        try:
            if self.exists:
                method = self.cloudformation.update_stack
                stack_action = "updat"  # appends "ing", "e" or "ed" in log messages
            else:
                method = self.cloudformation.create_stack
                stack_action = "creat"

            logger.info("{}ing stack {}", stack_action.title(), self.name)

            method(
                StackName=self.name,
                TemplateURL=template_url,
                Parameters=[
                    {"ParameterKey": key, "ParameterValue": value}
                    for key, value in parameters.items()
                ],
                Tags=[{"Key": key, "Value": value} for key, value in tags.items()],
            )
        except ClientError as client_error:
            if (
                client_error.response["Error"]["Message"]
                == "No updates are to be performed."
            ):
                logger.info("No changes. Stack {} not updated", self.name)
                return

            raise client_error

        if wait:
            logger.info("Waiting for stack {} to {}e", self.name, stack_action)
            self.wait()

            stack_status = self.status

            if stack_status not in SUCCESSFUL_STACK_STATUSES:
                raise Exception(
                    f"Stack did not {stack_action}e successfully: {self.name} is in {stack_status} status"
                )

            logger.info("Successfully {}ed stack {}", stack_action, self.name)

    def wait(self):
        """Waits for a stack create/update to complete, logging each event while waiting"""
        stack_status = self.status
        events = self.events()

        event_ids = [event["EventId"] for event in events]

        for event in reversed(events[:1]):
            log_event(
                event["LogicalResourceId"],
                event["ResourceStatus"],
                event.get("ResourceStatusReason", None),
            )

        while stack_status in IN_PROGRESS_STACK_STATUSES:
            events = filter(
                lambda event: event["EventId"] not in event_ids,
                reversed(self.events()),
            )

            for event in events:
                log_event(
                    event["LogicalResourceId"],
                    event["ResourceStatus"],
                    event.get("ResourceStatusReason", None),
                )
                event_ids.append(event["EventId"])

            stack_status = self.status

            time.sleep(5)

    def events(self) -> Dict:
        stack_events = self.cloudformation.describe_stack_events(StackName=self.name)

        return stack_events["StackEvents"]

    def __describe(self) -> Dict:
        stack_data = self.cloudformation.describe_stacks(StackName=self.name)

        return stack_data["Stacks"][0]
