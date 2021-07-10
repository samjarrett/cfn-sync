import io
import os
from unittest.mock import MagicMock, patch

from cfn_sync import cli
from cfn_sync.stack import Stack


def test_parse_args_deploy():
    """Tests parse_args() deploy"""
    template_file = os.path.join(os.path.dirname(__file__), "demo.yml")

    args = cli.parse_args(
        [
            "deploy",
            "--stack-name",
            "my-stack",
            "--template-file",
            template_file,
        ]
    )
    assert args.action == "deploy"
    assert args.func == cli.deploy  # pylint: disable=comparison-with-callable
    assert args.stack_name == "my-stack"
    assert isinstance(args.template_file, io.TextIOWrapper)
    assert args.template_file.name == template_file
    assert args.parameters == {}
    assert args.tags == {}
    assert args.capabilities == []

    args = cli.parse_args(
        [
            "deploy",
            "--stack-name",
            "my-stack",
            "--template-file",
            template_file,
            "--parameter-overrides",
            "MyParam=MyVal",
            "ParamTwo=ValueTwo",
            "--tags",
            "TagOne=TagVal",
            "TagTwo=ValueTwo",
        ]
    )
    assert args.action == "deploy"
    assert args.parameters == {"MyParam": "MyVal", "ParamTwo": "ValueTwo"}
    assert args.tags == {"TagOne": "TagVal", "TagTwo": "ValueTwo"}

    args = cli.parse_args(
        [
            "deploy",
            "--stack-name",
            "my-stack",
            "--template-file",
            template_file,
            "--capabilities",
            "CAPABILITY_NAMED_IAM",
            "CAPABILITY_TWO",
        ]
    )
    assert args.capabilities == ["CAPABILITY_NAMED_IAM", "CAPABILITY_TWO"]


def test_parse_args_delete():
    """Tests parse_args() delete"""
    args = cli.parse_args(["delete", "--stack-name", "my-stack"])
    assert args.action == "delete"
    assert args.func == cli.delete  # pylint: disable=comparison-with-callable
    assert args.stack_name == "my-stack"


@patch("cfn_sync.direct_deployer.deploy")
def test_deploy(deploy_mock: MagicMock, stack: Stack):
    """Tests deploy()"""
    template = io.StringIO("hello")
    cli.deploy(stack, template, {}, {}, [])
    deploy_mock.assert_called_once_with(stack, "hello", {}, {})

    deploy_mock.reset_mock()
    cli.deploy(stack, template, {}, {}, ["CAPABILITY_ONE"])
    assert stack.capabilities == ["CAPABILITY_ONE"]


@patch("cfn_sync.deleter.delete")
def test_delete(delete_mock: MagicMock, stack: Stack):
    """Tests delete()"""
    cli.delete(stack)
    delete_mock.assert_called_once_with(stack)
