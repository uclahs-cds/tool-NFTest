""" NF Test assert """
import errno
import os
from pathlib import Path
import subprocess as sp
from typing import Callable
from nftest.common import calculate_checksum


class NFTestAssert():
    """ Defines how nextflow test results are asserted. """
    def __init__(self, actual:str, expect:str, method:str='md5',
            script:str=None):
        """ Constructor """
        self.actual = actual
        self.expect = expect
        self.method = method
        self.script = script

    def assert_expected(self):
        """ Assert the results match with the expected values. """
        if not Path(self.actual).exists():
            print(f'Actual file not found: {self.actual}')
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                self.actual)

        if not Path(self.expect).exists():
            print(f'Expect file not found: {self.actual}')
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                self.expect)

        assert_method = self.get_assert_method()
        try:
            assert assert_method(self.actual, self.expect)
        except AssertionError as error:
            print('Assertion failed\n', flush=True)
            print(f'Actual: {self.actual}\n', flush=True)
            print(f'Expect: {self.expect}\n', flush=True)
            raise error

    def get_assert_method(self) -> Callable:
        """ Get the assert method """
        # pylint: disable=E0102
        if self.script is not None:
            def func(actual, expect):
                cmd = f"{self.script} {actual} {expect}"
                process_out = sp.run(cmd, shell=True, check=False)
                return process_out.returncode == 0
            return func
        if self.method == 'md5':
            def func(actual, expect):
                actual_value = calculate_checksum(actual)
                expect_value = calculate_checksum(expect)
                return actual_value == expect_value
            return func
        raise ValueError(f'assert method {self.method} unknown.')
