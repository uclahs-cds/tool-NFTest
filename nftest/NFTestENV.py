"""Environment variables"""

import os
import datetime
from dataclasses import dataclass, field, InitVar
from dotenv import load_dotenv
from nftest.Singleton import Singleton


@dataclass
class NFTestENV(metaclass=Singleton):
    """Class for initializng and holding environment variables."""

    # pylint: disable=invalid-name
    NFT_OUTPUT: str = field(init=False)
    NFT_TEMP: str = field(init=False)
    NFT_INIT: str = field(init=False)
    NFT_PIPELINE: str = field(init=False)
    NFT_TESTDIR: str = field(init=False)
    NFT_LOG_LEVEL: str = field(init=False)
    NFT_LOG: str = field(init=False)
    test_yaml: InitVar[str]

    def __post_init__(self, test_yaml: str = None):
        """Post-init set env variables"""
        yaml_dir = os.path.abspath(os.path.dirname(test_yaml)) if test_yaml else None

        NFTestENV.load_env(yaml_dir)

        self.NFT_OUTPUT = os.getenv("NFT_OUTPUT", default="./")
        self.NFT_TEMP = os.getenv("NFT_TEMP", default="./")
        self.NFT_INIT = os.getenv("NFT_INIT", default=str(os.getcwd()))
        self.NFT_PIPELINE = os.getenv("NFT_PIPELINE", default=self.NFT_INIT)
        self.NFT_TESTDIR = os.getenv("NFT_TESTDIR", default=yaml_dir)
        self.NFT_LOG_LEVEL = os.getenv("NFT_LOG_LEVEL", default="INFO")
        self.NFT_LOG = os.getenv(
            "NFT_LOG",
            default=os.path.join(
                self.NFT_OUTPUT,
                f'log-nftest-{datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.log',
            ),
        )

    @staticmethod
    def load_env(yaml_dir: str = None):
        """Load and set env variables"""
        dirs_to_check = []
        dirs_to_check.append(os.getcwd())
        dirs_to_check.append(os.path.expanduser("~"))
        if yaml_dir:
            dirs_to_check.append(yaml_dir)
        for adir in dirs_to_check:
            if not load_dotenv(os.path.join(adir, ".env")):
                print(f"LOG: .env not found in {adir}.", flush=True)
            else:
                print(f"LOG: Loaded .env from {adir}", flush=True)
                return

        print(
            "WARN: unable to find .env. Default values and existing variables will be used.",
            flush=True)
