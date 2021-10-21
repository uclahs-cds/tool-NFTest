""" NF Test case """
from __future__ import annotations
import shutil
import subprocess as sp
from typing import Callable, List, TYPE_CHECKING
from nftest.common import remove_nextflow_logs


if TYPE_CHECKING:
    from nftest.NFTestGlobal import NFTestGlobal
    from nftest.NFTestAssert import NFTestAssert

class NFTestCase():
    """ Defines the NF test case """
    # pylint: disable=R0902
    # pylint: disable=R0913
    def __init__(self, name:str=None, message:str=None, nf_script:str=None,
            nf_configs:List[str]=None, asserts:List[NFTestAssert]=None,
            temp_dir:str=None, remove_temp:bool=None, clean_logs:bool=True,
            skip:bool=False, verbose:bool=False):
        """ Constructor """
        self.name = name
        self.message = message
        self.nf_script = nf_script
        self.nf_configs = nf_configs or []
        self.asserts = asserts or []
        self.temp_dir = temp_dir
        self.remove_temp = remove_temp
        self.clean_logs = clean_logs
        self.skip = skip
        self.verbose = verbose

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
            print(' [ skipped ]\n', flush=True)
            return
        res = self.submit()
        if res.returncode != 0:
            print(' [ failed ]\n', flush=True)
            return
        for ass in self.asserts:
            try:
                ass.assert_expected()
            except Exception as error:
                print(error.args, flush=True)
                print(' [ failed ]\n', flush=True)
                raise error
        print(' [ succeed ]\n', flush=True)

    def submit(self) -> sp.CompletedProcess:
        """ Submit a nextflow run """
        config_arg = ''
        for nf_config in self.nf_configs:
            config_arg += f'-c {nf_config} '
        cmd = f"""
        NXF_WORK={self.temp_dir} \
        nextflow run \
            {self.nf_script} \
            {config_arg}
        """
        print(' '.join(cmd.split()), flush=True)
        return sp.run(cmd, shell=True, check=False, capture_output=(not self.verbose))


    def combine_global(self, _global:NFTestGlobal) -> None:
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

        if not self.clean_logs:
            self.clean_logs = _global.clean_logs

    def print_prolog(self):
        """ Print prolog message """
        prolog = f'{self.name}: {self.message}'
        print(prolog, flush=True)
