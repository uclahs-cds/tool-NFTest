""" Global settings """


class NFTestGlobal():
    """ Test global settings """
    # pylint: disable=R0903
    def __init__(self, temp_dir:str, nf_config:str, remove_temp:bool=True,
            clean_logs:bool=True):
        """ constructor """
        self.temp_dir = temp_dir
        self.nf_config = nf_config
        self.remove_temp = remove_temp
        self.clean_logs = clean_logs
