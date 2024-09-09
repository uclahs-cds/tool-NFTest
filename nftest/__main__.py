"""Test NF-pipelines"""

from __future__ import annotations
import argparse
import sys
from logging import getLogger
from pathlib import Path
import shutil
import pkg_resources
from nftest.common import find_config_yaml, print_version_and_exist, setup_loggers
from nftest.NFTestRunner import NFTestRunner
from nftest.NFTestENV import NFTestENV


def parse_args() -> argparse.Namespace:
    """Parse args"""
    parser = argparse.ArgumentParser(prog="nftest")
    parser.add_argument(
        "-V", "--version", help="Version", action="store_true", default=False
    )

    subparsers = parser.add_subparsers(dest="command")
    add_subparser_init(subparsers)
    add_subparser_run(subparsers)

    args = parser.parse_args()

    if args.version:
        print_version_and_exist()

    if not hasattr(args, "func"):
        parser.print_usage()
        sys.exit(1)

    return args


def add_subparser_init(subparsers: argparse._SubParsersAction):
    """Add subparser for init"""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        name="init",
        help="Initialize nftest.",
        description="Initialize nftest by creating a nftest.yaml template.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.set_defaults(func=init)


def add_subparser_run(subparsers: argparse._SubParsersAction):
    """Add subparser for run"""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        name="run",
        help="Run nextflow tests.",
        description="Run nextflow tests.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--config-file",
        type=Path,
        help="Path to the nextflow test config YAML file. If not given, it"
        " looks for nftest.yaml or nftest.yml",
        default=None,
        nargs="?",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Save out a detailed JSON test report alongside the log file"
    )
    parser.add_argument(
        "TEST_CASES", type=str, help="Exact test case to run.", nargs="*"
    )
    parser.set_defaults(func=run)


def run(args):
    """Run"""
    find_config_yaml(args)
    setup_loggers()
    runner = NFTestRunner(args.report)
    runner.load_from_config(args.config_file, args.TEST_CASES)
    sys.exit(runner.main())


def init(_):
    """Set up nftest"""
    _env = NFTestENV()
    setup_loggers()
    _logger = getLogger("NFTestInit")

    working_dir = Path(_env.NFT_INIT)

    if not working_dir.exists():
        try:
            _logger.warning(
                "%s does not exist, attempting to create it...", working_dir
            )
            working_dir.mkdir(parents=True)
        except (OSError, PermissionError) as file_error:
            raise RuntimeError(
                f"Failed to create {working_dir}. "
                "Please ensure proper permissions are set."
            ) from file_error

    # copy over the nftest.yaml
    nftest_yaml = pkg_resources.resource_filename("nftest", "data/nftest.yml")
    if not (working_dir / "nftest.yml").exists():
        test_yaml = shutil.copy2(nftest_yaml, working_dir)
        _logger.info("%s created", test_yaml)
    else:
        _logger.info("%s/nftest.yml already exists", working_dir)

    # copy global.config over
    global_config = pkg_resources.resource_filename("nftest", "data/global.config")
    test_dir = working_dir / "test"
    test_dir.mkdir(exist_ok=True)
    if not (test_dir / "global.config").exists():
        global_config = shutil.copy2(global_config, test_dir / "global.config")
        _logger.info("%s created", global_config)
    else:
        _logger.info("%s/global.config already exists", test_dir)


def main():
    """main entrance"""
    args = parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
