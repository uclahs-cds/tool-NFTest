""" NF Test case """
from __future__ import annotations

import re
import selectors
import shutil
import subprocess as sp

from logging import getLogger, INFO, ERROR
from pathlib import Path
from shlex import quote
from subprocess import PIPE
from typing import Callable, List, TYPE_CHECKING

from nftest.common import remove_nextflow_logs
from nftest.NFTestENV import NFTestENV


if TYPE_CHECKING:
    from nftest.NFTestGlobal import NFTestGlobal
    from nftest.NFTestAssert import NFTestAssert

class NFTestCase():
    """ Defines the NF test case """
    # pylint: disable=R0902
    # pylint: disable=R0913
    def __init__(self, name:str=None, message:str=None, nf_script:str=None,
            nf_configs:List[str]=None, profiles:List[str]=None, params_file:str=None,
            output_directory_param_name:str='output_dir',
            asserts:List[NFTestAssert]=None, temp_dir:str=None,
            remove_temp:bool=None, clean_logs:bool=None,
            skip:bool=False, verbose:bool=False):
        """ Constructor """
        self._env = NFTestENV()
        self._logger = getLogger('NFTest')
        self._nflogger = getLogger("NextFlow")
        self.name = name
        self.name_for_output = re.sub(r'[^a-zA-Z0-9_\-.]', '', self.name.replace(' ', '-'))
        self.message = message
        self.nf_script = nf_script
        self.nf_configs = nf_configs or []
        self.profiles = profiles or []
        self.params_file = params_file
        self.output_directory_param_name = output_directory_param_name
        self.asserts = self.resolve_actual(asserts)
        self.temp_dir = temp_dir
        self.remove_temp = remove_temp
        self.clean_logs = clean_logs
        self.skip = skip
        self.verbose = verbose

    def resolve_actual(self, asserts:List[NFTestAssert]=None):
        """ Resolve the file path for actual file """
        if not asserts:
            return []

        for assertion in asserts:
            assertion.actual = str(
                Path(self._env.NFT_OUTPUT)/self.name_for_output/assertion.actual)

        return asserts

    # pylint: disable=E0213
    def test_wrapper(func:Callable):
        """ Wrap tests with additional logging and cleaning. """
        def wrapper(self):
            # pylint: disable=E1102
            self.print_prolog()
            func(self)
            if self.remove_temp:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            if self.clean_logs:
                remove_nextflow_logs()
        return wrapper

    @test_wrapper
    def test(self):
        """ Run test cases. """
        if self.skip:
            self._logger.info(' [ skipped ]')
            return
        res = self.submit()
        if res.returncode != 0:
            self._logger.error(' [ failed ]')
            return
        for ass in self.asserts:
            try:
                ass.identify_assertion_files()
                ass.assert_exists()
                ass.assert_updated()
                ass.assert_expected()
            except Exception as error:
                self._logger.error(error.args)
                self._logger.error(' [ failed ]')
                raise error
        self._logger.info(' [ succeed ]')

    def submit(self) -> sp.CompletedProcess:
        """ Submit a nextflow run """
        config_arg = ''
        if self.nf_configs:
            config_arg = '-c ' + ' -c '.join(self.nf_configs)
        params_file_arg = f"-params-file {self.params_file}" if self.params_file else ""
        profiles_arg = f"-profile {quote(','.join(self.profiles))}" if self.profiles else ""
        output_directory_with_case = Path(self._env.NFT_OUTPUT)/self.name_for_output
        output_directory_arg = f"--{self.output_directory_param_name} " \
            f"{output_directory_with_case}"
        cmd = f"""
        NXF_WORK={self.temp_dir} \
        nextflow run \
            {self.nf_script} \
            {profiles_arg} \
            {config_arg} \
            {params_file_arg} \
            {output_directory_arg}
        """
        self._logger.info(' '.join(cmd.split()))

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
                    data=INFO
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
                            self._nflogger.log(
                                level=key.data,
                                msg=line.rstrip()
                            )

        return process

    def combine_global(self, _global: NFTestGlobal) -> None:
        """ Combine test case configs with the global configs. """
        if _global.nf_config:
            self.nf_configs.insert(0, _global.nf_config)

        if self.remove_temp is None:
            if _global.remove_temp:
                self.remove_temp = _global.remove_temp
            else:
                self.remove_temp = False

        if not self.temp_dir:
            self.temp_dir = _global.temp_dir

        if self.clean_logs is None:
            self.clean_logs = _global.clean_logs

    def print_prolog(self):
        """ Print prolog message """
        prolog = f'{self.name}: {self.message}'
        self._logger.info(prolog)
