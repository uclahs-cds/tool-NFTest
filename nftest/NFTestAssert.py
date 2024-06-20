"""NF Test assert"""

import datetime
import errno
import os
import subprocess
from typing import Callable
from logging import getLogger, DEBUG

from nftest.common import calculate_checksum, resolve_single_path, popen_with_logger
from nftest.NFTestENV import NFTestENV


class NFTestAssert:
    """Defines how nextflow test results are asserted."""

    def __init__(
        self, actual: str, expect: str, method: str = "md5", script: str = None
    ):
        """Constructor"""
        self._env = NFTestENV()
        self._logger = getLogger("NFTest")
        self.actual = actual
        self.expect = expect
        self.method = method
        self.script = script

        self.startup_time = datetime.datetime.now(tz=datetime.timezone.utc)

    def identify_assertion_files(self) -> None:
        """Resolve actual and expected paths"""
        self.actual = resolve_single_path(self.actual)
        self.expect = resolve_single_path(self.expect)

    def assert_exists(self) -> None:
        "Assert that the expected and actual files exist."
        if not self.actual.exists():
            self._logger.error("Actual file not found: %s", self.actual)
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.actual
            )

        if not self.expect.exists():
            self._logger.error("Expect file not found: %s", self.expect)
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.expect
            )

    def assert_updated(self) -> None:
        "Assert that the actual file was updated during this test run."
        file_mod_time = datetime.datetime.fromtimestamp(
            self.actual.stat().st_mtime, tz=datetime.timezone.utc
        )

        self._logger.debug("Test creation time: %s", self.startup_time)
        self._logger.debug("Actual mod time:    %s", file_mod_time)
        assert (
            file_mod_time > self.startup_time
        ), f"{str(self.actual)} was not modified by this pipeline"

    def assert_expected(self) -> None:
        "Assert the results match with the expected values."
        assert_method = self.get_assert_method()
        try:
            assert assert_method(self.actual, self.expect)
            self._logger.debug("Assertion passed")
        except AssertionError as error:
            self._logger.error("Assertion failed")
            self._logger.error("Actual: %s", self.actual)
            self._logger.error("Expect: %s", self.expect)
            raise error

    def get_assert_method(self) -> Callable:
        """Get the assert method"""
        if self.script is not None:
            def script_function(actual, expect):
                cmd = [self.script, actual, expect]
                self._logger.debug(subprocess.list2cmdline(cmd))

                process = popen_with_logger(
                    cmd, logger=self._logger, stdout_level=DEBUG
                )
                return process.returncode == 0

            return script_function

        if self.method == "md5":
            def md5_function(actual, expect):
                self._logger.debug("md5 %s %s", actual, expect)
                actual_value = calculate_checksum(actual)
                expect_value = calculate_checksum(expect)
                return actual_value == expect_value

            return md5_function

        self._logger.error("assert method %s unknown.", self.method)
        raise ValueError(f"assert method {self.method} unknown.")
