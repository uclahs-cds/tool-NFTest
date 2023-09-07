""" Common functions """
import argparse
import hashlib
import glob
import os
import logging
from pathlib import Path
import shutil
import sys
import time
from nftest import __version__
from nftest.NFTestENV import NFTestENV

# pylint: disable=W0613
def validate_yaml(path:Path):
    """ Validate the yaml. Potentially use yaml schema
    https://rx.codesimply.com/
    """
    return True

def remove_nextflow_logs() -> None:
    """ Remove log files generated by nextflow """
    files = glob.glob('./.nextflow*')
    for file in files:
        if Path(file).is_dir():
            shutil.rmtree(file, ignore_errors=True)
        else:
            os.remove(file)

def calculate_checksum(path:Path) -> str:
    """ Calculate checksum recursively.
    Args:
        path (Path): The path to the directory.
        stdout (bool): If true, the result is printed to stdout.
    """
    sum_val = hashlib.md5()
    with open(path, "rb") as handle:
        for byte_block in iter(lambda: handle.read(4096), b""):
            sum_val.update(byte_block)
    sum_val = sum_val.hexdigest()
    return sum_val

def find_config_yaml(args:argparse.Namespace):
    """ Find the test config yaml """
    if args.config_file is None:
        if Path('./nftest.yaml').exists():
            args.config_file = Path('./nftest.yaml')
        elif Path('./nftest.yml').exists():
            args.config_file = Path('./nftest.yml')

def print_version_and_exist():
    """ print version and exist """
    print(__version__, file=sys.stdout)
    sys.exit()


def setup_loggers():
    """ Initialize loggers for both init and run """
    # Always log times in UTC
    logging.Formatter.converter = time.gmtime

    _env = NFTestENV()

    # Make a file handler that accepts all logs
    try:
        file_handler = logging.FileHandler(_env.NFT_LOG)
        file_handler.setLevel(logging.DEBUG)
    except (FileNotFoundError, PermissionError) as file_error:
        raise Exception(f'Unable to create log file: {_env.NFT_LOG}') from file_error

    # Make a stream handler with the requested verbosity
    stream_handler = logging.StreamHandler(sys.stdout)
    try:
        stream_handler.setLevel(logging._checkLevel(_env.NFT_LOG_LEVEL)) # pylint: disable=W0212
    except ValueError:
        stream_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=(file_handler, stream_handler)
    )
