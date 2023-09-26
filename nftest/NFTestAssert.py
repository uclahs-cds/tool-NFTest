""" NF Test assert """
import errno
import selectors
import os
from pathlib import Path
import subprocess as sp
from subprocess import PIPE
from typing import Callable
from logging import getLogger, DEBUG, ERROR
from nftest.common import calculate_checksum
from nftest.NFTestENV import NFTestENV


class NFTestAssert():
    """ Defines how nextflow test results are asserted. """
    def __init__(self, actual:str, expect:str, method:str='md5', script:str=None):
        """ Constructor """
        self._env = NFTestENV()
        self._logger = getLogger('NFTest')
        self.actual = actual
        self.expect = expect
        self.method = method
        self.script = script

    def assert_expected(self):
        """ Assert the results match with the expected values. """
        if not Path(self.actual).exists():
            self._logger.error('Actual file not found: %s', self.actual)
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                self.actual)

        if not Path(self.expect).exists():
            self._logger.error('Expect file not found: %s', self.expect)
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                self.expect)

        assert_method = self.get_assert_method()
        try:
            assert assert_method(self.actual, self.expect)
            self._logger.debug('Assertion passed')
        except AssertionError as error:
            self._logger.error('Assertion failed')
            self._logger.error('Actual: %s', self.actual)
            self._logger.error('Expect: %s', self.expect)
            raise error

    def get_assert_method(self) -> Callable:
        """ Get the assert method """
        # pylint: disable=E0102
        if self.script is not None:
            def func(actual, expect):
                cmd = f"{self.script} {actual} {expect}"
                self._logger.debug(cmd)
                with sp.Popen(cmd,
                              shell=True,
                              stdout=PIPE,
                              stderr=PIPE,
                              universal_newlines=True) as process:
                    # Route stdout to INFO and stderr to ERROR in real-time
                    with selectors.DefaultSelector() as selector:
                        selector.register(
                            fileobj=process.stdout,
                            events=selectors.EVENT_READ,
                            data=DEBUG
                        )
                        selector.register(
                            fileobj=process.stderr,
                            events=selectors.EVENT_READ,
                            data=ERROR
                        )

                        while process.poll() is None:
                            events = selector.select()
                            for key, _ in events:
                                line = key.fileobj.readline()
                                if line:
                                    # The only case in which this won't be true is when
                                    # the pipe is closed
                                    self._logger.log(
                                        level=key.data,
                                        msg=line.rstrip()
                                    )
                return process.returncode == 0
            return func
        if self.method == 'md5':
            def func(actual, expect):
                self._logger.debug("md5 %s %s", actual, expect)
                actual_value = calculate_checksum(actual)
                expect_value = calculate_checksum(expect)
                return actual_value == expect_value
            return func
        self._logger.error('assert method %s unknown.', self.method)
        raise ValueError(f'assert method {self.method} unknown.')
