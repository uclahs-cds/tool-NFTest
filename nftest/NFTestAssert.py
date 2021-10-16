""" NF Test assert """
import errno
import os
from pathlib import Path
from typing import Callable
from nftest.common import calculate_checksum


class NFTestAssert():
    """ Defines how nextflow test results are asserted. """
    def __init__(self, received:str, expected:str, method:str='md5',
            script:str=None):
        """ Constructor """
        self.received = received
        self.expected = expected
        self.method = method
        self.script = script

    def assert_expected(self):
        """ Assert the results match with the expected values. """
        if not Path(self.received).exists():
            print(f'Received file not found: {self.received}')
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                self.received)

        if not Path(self.expected).exists():
            print(f'Expected file not found: {self.received}')
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                self.expected)

        assert_method = self.get_assert_method()
        try:
            assert assert_method(self.received, self.expected)
        except AssertionError:
            print('Assertion failed\n', flush=True)
            print(f'Received: {self.received}\n', flush=True)
            print(f'Expected: {self.expected}\n', flush=True)

    def get_assert_method(self) -> Callable:
        """ Get the assert method """
        # pylint: disable=E0102
        if self.script is not None:
            def func(received, expected):
                cmd = f"{self.script} {received} {expected}"
                return sp.run(cmd, shell=True, check=False)
            return func
        if self.method == 'md5':
            def func(received, expected):
                received_value = calculate_checksum(received)
                expected_value = calculate_checksum(expected)
                return received_value == expected_value
            return func
        raise ValueError(f'assert method {self.method} unknown.')
