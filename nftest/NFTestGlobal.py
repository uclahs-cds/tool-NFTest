""" Global settings """
import os

class NFTestGlobal():
    """ Test global settings """
    # pylint: disable=R0903
    def __init__(self, temp_dir:str, nf_config:str, remove_temp:bool=True,
            clean_logs:bool=True):
        """ constructor """
        base_temp_dir = os.getenv('TEST_TEMP_DIRECTORY', default='./')
        self.temp_dir = os.path.join(base_temp_dir, temp_dir)
        init_dir = os.getenv('TEST_SETUP_DIRECTORY', default='./')
        self.nf_config = os.path.join(init_dir, nf_config)
        self.remove_temp = remove_temp
        self.clean_logs = clean_logs
