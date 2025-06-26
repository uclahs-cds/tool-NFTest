"""Test runner"""

import shutil
import os
from logging import getLogger
from pathlib import Path
from typing import List
import yaml
from nftest.NFTestGlobal import NFTestGlobal
from nftest.NFTestAssert import NFTestAssert, NFTestAssertionError
from nftest.NFTestCase import NFTestCase
from nftest.NFTestENV import NFTestENV
from nftest.NFTestReport import NFTestReport
from nftest.common import validate_yaml, validate_reference


class NFTestRunner:
    """This holds all test cases and global settings from a single yaml file."""

    def __init__(self, cases: List[NFTestCase] = None, report: bool = False):
        """Constructor"""
        self._global = None
        self._env = NFTestENV()
        self._logger = getLogger("NFTest")
        self.cases = cases or []
        self.save_report = report

    def combine_with_dir(self, path_to_combine: str, base_dir: str):
        """ Combine given path with NFT_INIT """
        if os.path.isabs(path_to_combine):
            self._logger.info(
                "`%s` is absolute. It will not be resolved relative to `%s`",
                path_to_combine, base_dir)

        return os.path.join(base_dir, path_to_combine)

    def resolve_testdir(self, config_yaml: str) -> str:
        """ Resolve directory containing test files """
        if self._env.NFT_TESTDIR:
            return self._env.NFT_TESTDIR

        return os.path.abspath(os.path.dirname(config_yaml))

    def load_from_config(self, config_yaml: str, target_cases: List[str]):
        """Load test info from config file."""
        validate_yaml(config_yaml)
        test_directory = self.resolve_testdir(config_yaml)
        with open(config_yaml, "rt", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
            self._global = NFTestGlobal(**config["global"])
            for case in config["cases"]:
                if "asserts" in case:
                    asserts = []
                    for ass in case["asserts"]:
                        if ass.get("script", None):
                            ass["script"] = self.combine_with_dir(ass["script"], test_directory)
                        asserts.append(NFTestAssert(**ass))
                else:
                    asserts = []
                case["asserts"] = asserts

                case["nf_script"] = (
                    self.combine_with_dir(case["nf_script"], self._env.NFT_PIPELINE)
                    if case.get("nf_script", None) else None
                )

                case_configs = [
                    self.combine_with_dir(case.pop("nf_config"), test_directory)
                ] if case.get("nf_config", None) else []

                for a_config in case.get("nf_configs", []):
                    case_configs.append(self.combine_with_dir(a_config, test_directory))

                case["nf_configs"] = case_configs

                case["params_file"] = (
                    self.combine_with_dir(case["params_file"], test_directory)
                    if case.get("params_file", None) else None
                )

                if "reference_files" in case:
                    case["reference_params"] = [
                        validate_reference(**reference_file)
                        for reference_file in case.pop("reference_files")
                    ]
                test_case = NFTestCase(**case)
                test_case.combine_global(self._global)
                if target_cases:
                    if test_case.name in target_cases:
                        test_case.skip = False
                    else:
                        continue
                self.cases.append(test_case)

    def main(self) -> int:
        """Main entrance"""
        self.print_prolog()

        failure_count = 0
        report = NFTestReport()

        for case in self.cases:
            with report.track_test(case):
                try:
                    if not case.test():
                        failure_count += 1
                except NFTestAssertionError as err:
                    # In case of failed test case, continue with other cases
                    self._logger.debug(err)
                    failure_count += 1
                except Exception as err:
                    # Unhandled error
                    self._logger.exception(err)
                    raise

        assert failure_count == len(report.failed_tests) + len(report.errored_tests)

        if self.save_report:
            report.write_report(Path(self._env.NFT_LOG).with_suffix(".json"))

        return failure_count

    def print_prolog(self):
        """Print prolog"""
        prolog = ""
        terminal_width = shutil.get_terminal_size().columns
        header = " NFTEST STARTS "
        half_width = int((terminal_width - len(header)) / 2)
        prolog = (
            "=" * half_width
            + header
            + "=" * (terminal_width - len(header) - half_width)
        )
        print(prolog, flush=True)
        self._logger.info("Beginning tests...")
