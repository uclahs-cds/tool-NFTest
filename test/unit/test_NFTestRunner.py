"""Test module for NFTestRunner"""

from dataclasses import dataclass
from unittest.mock import mock_open
import mock
from nftest.NFTestRunner import NFTestRunner


@dataclass
class RunnerData:
    """Basic dataclass for holding runner data"""
    # pylint: disable=unused-argument

    _global = None
    cases = []

    def resolve_testdir(self, yaml_dir):
        """ Identify path containing test directory """
        return None

    def combine_with_dir(self, file_to_combine, base_dir):
        """ Combine relative file path with base directory """
        return None


# pylint: disable=W0613
@mock.patch("nftest.NFTestRunner.NFTestCase")
@mock.patch("nftest.NFTestRunner.yaml.safe_load")
@mock.patch("nftest.NFTestRunner.validate_yaml")
@mock.patch("nftest.NFTestRunner.NFTestGlobal")
@mock.patch("nftest.NFTestRunner.open", new_callable=mock_open)
@mock.patch("nftest.NFTestRunner.NFTestRunner", wraps=NFTestRunner)
def test_load_from_config(
    mock_runner, mock_runner_open, mock_global, mock_validate_yaml, mock_yaml, mock_case
):
    """Tests for loading from config file"""
    mock_validate_yaml.return_value = lambda x: True
    mock_global.return_value = lambda: None
    mock_runner.return_value.NFTestGlobal = lambda: None
    mock_yaml.return_value = {
        "global": {},
        "cases": [
            {"name": "case1", "nf_config": None},
            {"name": "case2", "nf_config": None},
        ],
    }
    mock_case.return_value = lambda **kwargs: kwargs["name"]
    mock_case.return_value.combine_global = lambda x: None
    mock_runner.return_value.load_from_config = NFTestRunner.load_from_config

    runner = mock_runner()
    runner_data = RunnerData()
    runner.load_from_config(runner_data, "None", None)

    assert len(runner_data.cases) == 2
