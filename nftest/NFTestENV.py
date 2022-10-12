""" Environment variables """
import os
from dotenv import load_dotenv
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
        NFTestENV.load_env()

        self.NFT_OUTPUT = os.getenv('NFT_OUTPUT', default='./')
        self.NFT_TEMP = os.getenv('NFT_TEMP', default='./')
        self.NFT_INIT = os.getenv('NFT_INIT', default=str(os.getcwd()))

    @staticmethod
    def load_env():
        """ Load and set env variables """
        dirs_to_check = []
        dirs_to_check.append(os.getcwd())
        dirs_to_check.append(os.path.expanduser('~'))
        for adir in dirs_to_check:
            if not load_dotenv(os.path.join(adir, '.env')):
                print(f'LOG: .env not found in {adir}.')
            else:
                print(f'LOG: Loaded .env from {adir}')
                return

        print('WARN: unable to find .env. Default values will be used.')
