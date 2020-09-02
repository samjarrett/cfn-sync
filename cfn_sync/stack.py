import logging
import time
from typing import TYPE_CHECKING, Dict, List, Optional

from botocore.exceptions import ClientError  # type: ignore

if TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_cloudformation.client import CloudFormationClient
    from mypy_boto3_cloudformation.type_defs import ParameterTypeDef, TagTypeDef
else:
    CloudFormationClient = object
    ParameterTypeDef = object
    TagTypeDef = object

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
DEFAULT_WAIT_DELAY = 5

logger = logging.getLogger(__name__)


def log_event(
    logical_resource_id: str, resource_status: str, status_reason: Optional[str] = None
):
    """Formats and logs a CloudFormation stack event"""
    log_message = f"{logical_resource_id} - {resource_status}"
    if status_reason:
        log_message += f" - {status_reason}"

    logger.info(log_message)


def parameter_dict_to_list(parameters: Dict[str, str]) -> List[ParameterTypeDef]:
    """Convert parameter dictionary to CloudFormation's list[dict] format"""
    return [
        {"ParameterKey": key, "ParameterValue": value}
        for key, value in parameters.items()
    ]


def tag_dict_to_list(tags: Dict[str, str]) -> List[TagTypeDef]:
    """Convert parameter dictionary to CloudFormation's list[dict] format"""
    return [{"Key": key, "Value": value} for key, value in tags.items()]


class Stack:
    """Class that holds information about a CloudFormation stack"""

    cloudformation: CloudFormationClient
    name: str
    id: Optional[str] = None
    capabilities: Optional[List] = None
    wait_delay: int

    def __init__(
        self,
        cloudformation: CloudFormationClient,
        name: str,
        wait_delay: int = DEFAULT_WAIT_DELAY,
    ):
        self.cloudformation = cloudformation
        self.name = name
        self.wait_delay = wait_delay

    @property
    def identifier(self) -> str:
        """Retrieves the stack's best known identifier (StackId preference, Name fallback)"""
        return self.id or self.name

    @property
    def status(self) -> str:
        """Retrieves the stack's current status"""
        return self.describe()["StackStatus"]

    @property
    def parameters(self) -> Dict[str, str]:
        """Retrieves the stack's current parameters"""
        return {
            row["ParameterKey"]: row["ParameterValue"]
            for row in self.describe().get("Parameters", [])
        }

    @property
    def tags(self) -> Dict[str, str]:
        """Retrieves the stack's current tags"""
        return {row["Key"]: row["Value"] for row in self.describe().get("Tags", [])}

    @property
    def exists(self) -> bool:
        """Checks if the stack currently exists or not"""
        try:
            self.describe()

            return True
        except ClientError as exception:
            if "does not exist" in str(exception):
                return False

            raise

    def set_capabilities(self, capabilities: List):
        """Sets the capabilities to apply to the stack during deploy [create/update] actions"""
        self.capabilities = capabilities

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
            time.sleep(self.wait_delay)

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
        stack_events = self.cloudformation.describe_stack_events(
            StackName=self.identifier
        )

        return stack_events["StackEvents"]  # type: ignore

    def describe(self) -> Dict:
        """Call CloudFormation DescribeStack"""
        stack_data = self.cloudformation.describe_stacks(StackName=self.identifier)

        return stack_data["Stacks"][0]  # type: ignore
