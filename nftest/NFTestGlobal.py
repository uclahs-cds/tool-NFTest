"""Global settings"""

import os
from nftest.NFTestENV import NFTestENV


class NFTestGlobal:
    """Test global settings"""

    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        temp_dir: str,
        nf_config: str,
        remove_temp: bool = True,
        clean_logs: bool = True,
    ):
        """constructor"""
        self._env = NFTestENV()
        self.temp_dir = os.path.join(self._env.NFT_TEMP, temp_dir)
        self.nf_config = os.path.join(self._env.NFT_PIPELINE, nf_config)
        self.remove_temp = remove_temp
        self.clean_logs = clean_logs
