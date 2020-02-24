import argparse
from collections import ChainMap
from copy import copy
from io import TextIOWrapper
import logging
import sys
from typing import List

import boto3
from botocore.exceptions import ClientError  # type: ignore

from .cloudformation import Stack


def split_key_equals_value(value: str):
    """Split key=value strings into a dictionary of key: value"""
    if "=" not in value:
        raise Exception("Format is KEY=VALUE")

    separated = value.split("=")
    return {separated[0]: separated[1]}


def deploy(
    stack: Stack,
    template_file: TextIOWrapper,
    parameters: List,
    tags: List,
    capabilities: List,
):
    """Deploy the CloudFormation stack"""
    parameter_dict = dict(ChainMap(*parameters))
    tag_dict = dict(ChainMap(*tags))

    if capabilities:
        stack.set_capabilities(capabilities)

    stack.deploy(template_file.read(), parameter_dict, tag_dict)


def delete(stack: Stack):
    """Delete the CloudFormation stack"""
    stack.delete()


def main():
    """The main CLI entrypoint"""
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M", format="[%(asctime)s] %(levelname)-2s: %(message)s"
    )

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        required=True,
        help="The action to perform on the CloudFormation stack",
        title="subcommands",
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
        nargs="+",
        type=split_key_equals_value,
        help="A list of parameter structures that specify input parameters for your stack template. If you're updating"
        " a stack and you don't specify a parameter, the command uses the stack's existing value. For new stacks, you"
        " must specify parameters that don't have a default value. Syntax: ParameterKey1=ParameterValue1"
        " ParameterKey2=ParameterValue2",
        metavar="ParameterKey=ParameterValue",
        default=[],
    )
    parser_deploy.add_argument(
        "--tags",
        nargs="+",
        type=split_key_equals_value,
        help="A list of tags to associate with the stack that is created or updated. AWS CloudFormation also propagates"
        " these tags to resources in the stack if the resource supports it. Syntax:TagKey1=TagValue1 TagKey2=TagValue2",
        metavar="TagKey=TagValue",
        default=[],
    )
    parser_deploy.add_argument(
        "--capabilities",
        nargs="+",
        type=str,
        help="A list of capabilities that you must specify before AWS Cloudformation can create certain stacks.",
        default=[],
    )

    parser_delete = subparsers.add_parser("delete", help="Delete CloudFormation stack")
    parser_delete.set_defaults(func=delete)
    parser_delete.add_argument(
        "--stack-name",
        type=str,
        help="The name or the unique stack ID that is associated with the stack.",
        required=True,
    )

    args = vars(parser.parse_args())

    func = args.pop("func")
    stack_name = args.pop("stack_name")

    stack = Stack(boto3.client("cloudformation"), stack_name)

    try:
        func(stack=stack, **args)

    except ClientError as exception:
        sys.exit(exception)


if __name__ == "__main__":  # pragma: no cover
    main()
