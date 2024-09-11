"""NF Test assert"""

import datetime
import glob
import subprocess
from typing import Callable, Optional
from logging import getLogger, DEBUG

from pathlib import Path

from nftest.common import calculate_checksum, popen_with_logger
from nftest.NFTestENV import NFTestENV


class NFTestAssertionError(Exception):
    """Base class for assertions."""


class NotUpdatedError(NFTestAssertionError):
    """An exception indicating that file was not updated."""
    def __init__(self, path: Path):
        self.path = path

    def __str__(self) -> str:
        return f"{self.path} was not modified by this pipeline"

class MismatchedContentsError(NFTestAssertionError):
    """An exception that the contents are mismatched."""
    def __init__(self, actual: Path, expect: Path):
        self.actual = actual
        self.expect = expect

    def __str__(self) -> str:
        return f"File comparison failed between {self.actual} and {self.expect}"

class NonSpecificGlobError(NFTestAssertionError):
    """An exception that the glob did not resolve to a single file."""
    def __init__(self, globstr: str, paths: list[str]):
        self.globstr = globstr
        self.paths = paths

    def __str__(self) -> str:
        if self.paths:
            return f"Expression `{self.globstr}` resolved to multiple files: {self.paths}"

        return f"Expression `{self.globstr}` did not resolve to any files"


def resolve_single_path(path: str) -> Path:
    """Resolve wildcards in path and ensure only a single path is identified"""
    expanded_paths = glob.glob(path)

    if len(expanded_paths) != 1:
        raise NonSpecificGlobError(path, expanded_paths)

    return Path(expanded_paths[0])


class NFTestAssert:
    """Defines how nextflow test results are asserted."""

    def __init__(
        self,
        actual: str,
        expect: str,
        method: str = "md5",
        script: Optional[str] = None,
    ):
        """Constructor"""
        self._env = NFTestENV()
        self._logger = getLogger("NFTest")
        self.actual = actual
        self.expect = expect
        self.method = method
        self.script = script

        self.startup_time = datetime.datetime.now(tz=datetime.timezone.utc)

    def perform_assertions(self):
        "Perform the appropriate assertions on the named files."
        # Ensure that there is exactly one file for each input glob pattern
        actual_path = resolve_single_path(self.actual)
        self._logger.debug(
            "Actual path `%s` resolved to `%s`", self.actual, actual_path
        )
        expect_path = resolve_single_path(self.expect)
        self._logger.debug(
            "Expected path `%s` resolved to `%s`", self.expect, expect_path
        )

        # Assert that the actual file was updated during this test run
        file_mod_time = datetime.datetime.fromtimestamp(
            actual_path.stat().st_mtime, tz=datetime.timezone.utc
        )

        self._logger.debug("Test creation time: %s", self.startup_time)
        self._logger.debug("Actual mod time:    %s", file_mod_time)

        if self.startup_time >= file_mod_time:
            raise NotUpdatedError(actual_path)

        # Assert that the files match
        if not self.get_assert_method()(actual_path, expect_path):
            self._logger.error("Assertion failed")
            self._logger.error("Actual: %s", self.actual)
            self._logger.error("Expect: %s", self.expect)
            raise MismatchedContentsError(actual_path, expect_path)

        self._logger.debug("Assertion passed")

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
        raise NFTestAssertionError(f"assert method {self.method} unknown.")
