"""Test runner"""

import shutil
from logging import getLogger
from typing import List
import yaml
from nftest.NFTestGlobal import NFTestGlobal
from nftest.NFTestAssert import NFTestAssert
from nftest.NFTestCase import NFTestCase
from nftest.NFTestENV import NFTestENV
from nftest.common import validate_yaml, validate_reference


class NFTestRunner:
    """This holds all test cases and global settings from a single yaml file."""

    def __init__(self, cases: List[NFTestCase] = None):
        """Constructor"""
        self._global = None
        self._env = NFTestENV()
        self._logger = getLogger('NFTest')
        self.cases = cases or []

    def load_from_config(self, config_yaml: str, target_cases: List[str]):
        """Load test info from config file."""
        validate_yaml(config_yaml)
        with open(config_yaml, 'rt', encoding='utf-8') as handle:
            config = yaml.safe_load(handle)
            self._global = NFTestGlobal(**config['global'])
            for case in config['cases']:
                if 'asserts' in case:
                    asserts = [NFTestAssert(**ass) for ass in case['asserts']]
                else:
                    asserts = []
                case['asserts'] = asserts
                case['nf_configs'] = (
                    [case.pop('nf_config')] if case.get('nf_config', None) else []
                )
                if 'reference_files' in case:
                    case['reference_params'] = [
                        validate_reference(**reference_file)
                        for reference_file in case.pop('reference_files')
                    ]
                test_case = NFTestCase(**case)
                test_case.combine_global(self._global)
                if target_cases:
                    if test_case.name in target_cases:
                        test_case.skip = False
                    else:
                        continue
                self.cases.append(test_case)

    def main(self):
        """Main entrance"""
        self.print_prolog()

        failure_count = 0

        for case in self.cases:
            try:
                if not case.test():
                    failure_count += 1
            except AssertionError:
                # In case of failed test case, continue with other cases
                failure_count += 1

        return failure_count

    def print_prolog(self):
        """Print prolog"""
        prolog = ''
        terminal_width = shutil.get_terminal_size().columns
        header = ' NFTEST STARTS '
        half_width = int((terminal_width - len(header)) / 2)
        prolog = (
            '=' * half_width
            + header
            + '=' * (terminal_width - len(header) - half_width)
        )
        print(prolog, flush=True)
        self._logger.info('Beginning tests...')
