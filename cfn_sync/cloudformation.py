import logging
import time
from typing import Dict, List, Optional

from mypy_boto3_cloudformation import CloudFormationClient
from botocore.exceptions import ClientError  # type: ignore

IN_PROGRESS_STACK_STATUSES = frozenset(
    {
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
    }
)

SUCCESSFUL_STACK_STATUSES = frozenset(
    {"CREATE_COMPLETE", "UPDATE_COMPLETE", "IMPORT_COMPLETE", "DELETE_COMPLETE"}
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def log_event(
    logical_resource_id: str, resource_status: str, status_reason: Optional[str] = None
):
    """Formats and logs a CloudFormation stack event"""
    log_message = f"{logical_resource_id} - {resource_status}"
    if status_reason:
        log_message += f" - {status_reason}"

    logger.info(log_message)


def log(message: str):
    """Logs a general message"""
    logger.info(message)


class Stack:
    """Class that holds information about a CloudFormation stack, and can perform updates to it"""

    name: str
    id: Optional[str]
    capabilities: Optional[List] = None

    def __init__(
        self, cloudformation: CloudFormationClient, name: str,
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

    def set_capabilities(self, capabilities: List):
        """Sets the capabilities to apply to the stack during deploy [create/update] actions"""
        self.capabilities = capabilities

    def deploy(
        self, template_body: str, parameters: Dict, tags: Dict, wait: bool = True,
    ):
        """Performs a create/update against the stack and optionally waits for it to stabilise"""
        try:
            if self.exists:
                logger.debug("Stack exists - setting method to update_stack")
                method = self.cloudformation.update_stack
            else:
                logger.debug("Stack does not exist - setting method to create_stack")
                method = self.cloudformation.create_stack  # type: ignore

            response = method(
                StackName=self.name,
                TemplateBody=template_body,
                Parameters=[
                    {"ParameterKey": key, "ParameterValue": value}
                    for key, value in parameters.items()
                ],
                Tags=[{"Key": key, "Value": value} for key, value in tags.items()],
                Capabilities=self.capabilities or [],
            )
            self.id = response["StackId"]
        except ClientError as client_error:
            if (
                client_error.response["Error"]["Message"]
                == "No updates are to be performed."
            ):
                log(f"No changes. Stack {self.name} not updated")
                return

            raise client_error

        if wait:
            self.wait()

            stack_status = self.status

            if stack_status not in SUCCESSFUL_STACK_STATUSES:
                raise Exception(
                    f"Stack did not deploy successfully: {self.name} is in {stack_status} status"
                )

    def delete(self, wait: bool = True):
        """Performs a delete against the stack and optionally waits for it to complete"""
        self.id = self.__describe()["StackId"]
        self.cloudformation.delete_stack(StackName=self.name)

        if wait:
            self.wait()

            stack_status = self.status

            if stack_status not in SUCCESSFUL_STACK_STATUSES:
                raise Exception(
                    f"Stack did not delete successfully: {self.name} is in {stack_status} status"
                )

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
            time.sleep(5)

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

    def events(self) -> Dict:
        """Get the first page of events for the stack"""
        described_name = getattr(self, "id", self.name)

        stack_events = self.cloudformation.describe_stack_events(
            StackName=described_name
        )

        return stack_events["StackEvents"]  # type: ignore

    def __describe(self) -> Dict:
        """Call CloudFormation DescribeStack"""
        described_name = getattr(self, "id", self.name)

        stack_data = self.cloudformation.describe_stacks(StackName=described_name)

        return stack_data["Stacks"][0]  # type: ignore
