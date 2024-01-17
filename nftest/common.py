""" Common functions """
import argparse
import re
from typing import Tuple
import glob
import hashlib
import logging
import os
import selectors
import shutil
import subprocess
import sys
import time

from pathlib import Path

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

def resolve_single_path(path:str) -> Path:
    """ Resolve wildcards in path and ensure only a single path is identified """
    expanded_paths = glob.glob(path)
    if 1 != len(expanded_paths):
        raise ValueError(f"Path `{path}` resolved to 0 or more than 1 file: {expanded_paths}." \
        " Assertion failed.")

    return Path(expanded_paths[0])

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

def validate_reference(
    reference_parameter_name:str,
    reference_parameter_path:str,
    reference_checksum:str,
    reference_checksum_type:str) -> Tuple[str, str]:
    """ Validate reference file and checksum """
    if not re.match(r'[a-zA-Z0-9_\-.]+$', reference_parameter_name):
        raise ValueError(f'Reference parameter name: `{reference_parameter_name}` is invalid. '
            f'Please use only alphanumeric, _, -, and . characters in parameter names.')

    _logger = logging.getLogger("NFTest")

    actual_checksum = calculate_checksum(Path(reference_parameter_path))

    if actual_checksum != reference_checksum:
        _logger.warning('Checksum for reference file: %s'
            '=%s - `%s` does not match expected checksum of `%s`',
            reference_parameter_name,
            reference_parameter_path,
            actual_checksum,
            reference_checksum)

    return (reference_parameter_name, reference_parameter_path)

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
        raise RuntimeError(f'Unable to create log file: {_env.NFT_LOG}') from file_error

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


def popen_with_logger(*args,
                      logger=None,
                      stdout_level=logging.INFO,
                      stderr_level=logging.ERROR,
                      **kwargs) -> subprocess.CompletedProcess:
    """
    Run a subprocess and stream the console outputs to a logger.
    """
    for badarg in ("stdout", "stderr", "universal_newlines"):
        if badarg in kwargs:
            raise ValueError(f"Argument {badarg} is not allowed")

    if logger is None:
        raise ValueError("A logger must be supplied!")

    kwargs.update({
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "universal_newlines": True
    })

    with subprocess.Popen(*args, **kwargs) as process:
        # Route stdout to INFO and stderr to ERROR in real-time
        with selectors.DefaultSelector() as selector:
            selector.register(
                fileobj=process.stdout,
                events=selectors.EVENT_READ,
                data=stdout_level
            )
            selector.register(
                fileobj=process.stderr,
                events=selectors.EVENT_READ,
                data=stderr_level
            )

            while process.poll() is None:
                events = selector.select()
                for key, _ in events:
                    line = key.fileobj.readline()
                    if line:
                        # The only case in which this won't be true is when
                        # the pipe is closed
                        logger.log(
                            level=key.data,
                            msg=line.rstrip()
                        )

    return process
