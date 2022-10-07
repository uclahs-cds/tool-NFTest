""" Global settings """
import os
from nftest.NFTestENV import NFTestENV

class NFTestGlobal():
    """ Test global settings """
    # pylint: disable=R0903
    def __init__(self, temp_dir:str, nf_config:str, remove_temp:bool=True,
        clean_logs:bool=True, _env:NFTestENV=None):
        """ constructor """
        self._env = _env or NFTestENV()
        self.temp_dir = os.path.join(self._env.NFT_TEMP, temp_dir)
        self.nf_config = os.path.join(self._env.NFT_INIT, nf_config)
        self.remove_temp = remove_temp
        self.clean_logs = clean_logs
