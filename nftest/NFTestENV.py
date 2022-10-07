""" Environment variables """
import os
from dataclasses import dataclass, field
from nftest.common import load_env

# pylint: disable=C0103
@dataclass
class NFTestENV():
    """ Class for initializng and holding environment variables.
    """
    NFT_OUTPUT: str = field(init=False)
    NFT_TEMP: str = field(init=False)
    NFT_INIT: str = field(init=False)

    def __post_init__(self):
        """ Post-init set env variables """
        load_env()

        self.NFT_OUTPUT = os.getenv('NFT_OUTPUT', default='./')
        self.NFT_TEMP = os.getenv('NFT_TEMP', default='./')
        self.NFT_INIT = os.getenv('NFT_INIT', default=str(os.getcwd()))
