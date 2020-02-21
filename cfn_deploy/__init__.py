import argparse
from collections import ChainMap


def split_key_equals_value(value: str):
    if "=" not in value:
        raise Exception("Format is KEY=VALUE")

    separated = value.split("=")
    return {separated[0]: separated[1]}


def deploy(namespace: argparse.Namespace):
    print("running deploy")


def delete(namespace: argparse.Namespace):
    print("running delete")


def main():
    """The main CLI entrypoint"""
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
        type=str,
        help="The path where your AWS CloudFormation template is located.",
        required=True,
    )
    parser_deploy.add_argument(
        "--parameter-overrides",
        nargs="+",
        type=split_key_equals_value,
        help="A list of parameter structures that specify input parameters for your stack template. If you're updating"
        " a stack and you don't specify a parameter, the command uses the stack's existing value. For new stacks, you"
        " must specify parameters that don't have a default value. Syntax: ParameterKey1=ParameterValue1"
        " ParameterKey2=ParameterValue2",
        metavar="ParameterKey=ParameterValue",
    )
    parser_deploy.add_argument(
        "--tags",
        nargs="+",
        type=str,
        help="A list of tags to associate with the stack that is created or updated. AWS CloudFormation also propagates"
        " these tags to resources in the stack if the resource supports it. Syntax:TagKey1=TagValue1 TagKey2=TagValue2",
        metavar="TagKey=TagValue",
    )

    parser_delete = subparsers.add_parser("delete", help="Delete CloudFormation stack")
    parser_delete.set_defaults(func=delete)
    parser_delete.add_argument("stack_name", type=int, help="stack name")

    args = parser.parse_args()

    print(args)

    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
