from .stack import SUCCESSFUL_STACK_STATUSES, Stack


def delete(stack: Stack, wait: bool = True):
    """Performs a delete against the stack and optionally waits for it to complete"""
    stack.id = stack.describe()["StackId"]
    stack.cloudformation.delete_stack(StackName=stack.name)

    if wait:
        stack.wait()

        stack_status = stack.status

        if stack_status not in SUCCESSFUL_STACK_STATUSES:
            raise Exception(
                f"Stack did not delete successfully: {stack.name} is in {stack_status} status"
            )
