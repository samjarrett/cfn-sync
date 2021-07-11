import argparse
import logging
import sys
from io import TextIOWrapper
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError  # type: ignore

from . import deleter, direct_deployer, change_set_deployer
from .stack import Stack


class ParseDict(argparse.Action):
    """Parse a KEY=VALUE string-list into a dictionary"""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values,
        option_string: Optional[str] = None,
    ):
        """Perform the parsing"""
        result = {}

        if values:
            for item in values:
                key, value = item.split("=", 1)
                result[key] = value

        setattr(namespace, self.dest, result)


def deploy(
    stack: Stack,
    template_file: TextIOWrapper,
    parameters: Dict[str, str],
    tags: Dict[str, str],
    capabilities: List,
    use_change_set: bool = False,
):
    """Deploy the CloudFormation stack"""
    if capabilities:
        stack.set_capabilities(capabilities)

    method = direct_deployer.deploy
    if use_change_set:
        method = change_set_deployer.deploy

    method(stack, template_file.read(), parameters, tags)


def delete(stack: Stack):
    """Delete the CloudFormation stack"""
    deleter.delete(stack)


def parse_args(args=None) -> argparse.Namespace:
    """Parse CLI arguments"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        required=True,
        help="The action to perform on the CloudFormation stack",
        title="subcommands",
        dest="action",
    )

    # create the parser for the "a" command
    parser_deploy = subparsers.add_parser("deploy", help="Deploy CloudFormation stack")
    parser_deploy.set_defaults(func=deploy)
    parser_deploy.add_argument(
        "--stack-name",
        type=str,
        help="The name of the AWS CloudFormation stack you're deploying to. If you specify an existing stack, the "
        "command updates the stack. If you specify a new stack, the command creates it.",
        required=True,
    )
    parser_deploy.add_argument(
        "--template-file",
        type=argparse.FileType("r"),
        help="The path where your AWS CloudFormation template is located.",
        required=True,
    )
    parser_deploy.add_argument(
        "--parameter-overrides",
        dest="parameters",
        action=ParseDict,
        nargs="+",
        help="A list of parameter structures that specify input parameters for your stack template. If you're updating"
        " a stack and you don't specify a parameter, the command uses the stack's existing value. For new stacks, you"
        " must specify parameters that don't have a default value. Syntax: ParameterKey1=ParameterValue1"
        " ParameterKey2=ParameterValue2",
        metavar="ParameterKey=ParameterValue",
        default=dict(),
    )
    parser_deploy.add_argument(
        "--tags",
        nargs="+",
        action=ParseDict,
        help="A list of tags to associate with the stack that is created or updated. AWS CloudFormation also propagates"
        " these tags to resources in the stack if the resource supports it. Syntax:TagKey1=TagValue1 TagKey2=TagValue2",
        metavar="TagKey=TagValue",
        default=dict(),
    )
    parser_deploy.add_argument(
        "--capabilities",
        nargs="+",
        type=str,
        help="A list of capabilities that you must specify before AWS Cloudformation can create certain stacks.",
        default=[],
    )
    parser_deploy.add_argument(
        "--use-change-set",
        action="store_true",
        help="Should the executor use change sets to perform the update?",
        default=False,
    )

    parser_delete = subparsers.add_parser("delete", help="Delete CloudFormation stack")
    parser_delete.set_defaults(func=delete)
    parser_delete.add_argument(
        "--stack-name",
        type=str,
        help="The name or the unique stack ID that is associated with the stack.",
        required=True,
    )

    return parser.parse_args(args)


def main():
    """The main CLI entrypoint"""
    cloudformation = boto3.client("cloudformation")
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M",
        format="[%(asctime)s] %(levelname)-2s: %(message)s",
        level=logging.INFO,
    )

    args = vars(parse_args())

    args.pop("action")
    func = args.pop("func")
    stack_name = args.pop("stack_name")

    stack = Stack(cloudformation, stack_name)

    try:
        func(stack=stack, **args)

    except ClientError as exception:
        sys.exit(exception)
