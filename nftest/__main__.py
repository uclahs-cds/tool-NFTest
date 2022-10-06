""" Test NF-pipelines """
from __future__ import annotations
import argparse
import os
from pathlib import Path
import shutil
import pkg_resources
from nftest.common import find_config_yaml, print_version_and_exist, load_env
from nftest.NFTestRunner import NFTestRunner


def parse_args() -> argparse.Namespace:
    """ Parse args """
    parser = argparse.ArgumentParser(
        prog='nftest'
    )
    parser.add_argument(
        '-V', '--version',
        help='Version',
        action='store_true',
        default=False
    )

    subparsers = parser.add_subparsers(dest='command')
    add_subparser_init(subparsers)
    add_subparser_run(subparsers)
    return parser.parse_args()

# pylint: disable=W0212
def add_subparser_init(subparsers:argparse._SubParsersAction):
    """ Add subparser for init """
    parser:argparse.ArgumentParser = subparsers.add_parser(
        name='init',
        help='Initialize nftest.',
        description='Initialize nftest by creating a nftest.yaml template.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.set_defaults(func=init)

def add_subparser_run(subparsers:argparse._SubParsersAction):
    """ Add subparser for run """
    parser:argparse.ArgumentParser = subparsers.add_parser(
        name='run',
        help='Run nextflow tests.',
        description='Run nextflow tests.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-c', '--config-file',
        type=Path,
        help='Path the the nextflow test config YAML file. If not given, it'
        ' looks for nftest.yaml or nftest.yml',
        default=None,
        nargs='?'
    )
    parser.add_argument(
        'TEST_CASES',
        type=str,
        help='Exact test case to run.',
        nargs='*'
    )
    parser.set_defaults(func=run)

def run(args):
    """ Run """
    load_env()

    find_config_yaml(args)
    runner = NFTestRunner()
    runner.load_from_config(args.config_file, args.TEST_CASES)
    runner.main()

def init(_):
    """ Set up nftest """
    load_env()

    working_dir = os.getenv('TEST_SETUP_DIRECTORY', default=os.getcwd())
    working_dir = Path(working_dir)

    if not working_dir.exists():
        try:
            print(f'{working_dir} does not exist, attempting to create it...')
            working_dir.mkdir(parents=True)
        except (OSError, PermissionError) as file_error:
            raise Exception(f'Failed to create {working_dir}. ' \
                'Please ensure proper permissions are set.') \
                from file_error

    # copy over the nftest.yaml
    nftest_yaml = pkg_resources.resource_filename(
        'nftest', 'data/nftest.yml'
    )
    if not (working_dir/'nftest.yml').exists():
        test_yaml = shutil.copy2(nftest_yaml, working_dir)
        print(f'{test_yaml} created', flush=True)
    else:
        print(f'{working_dir}/nftest.yml already exists', flush=True)

    # copy global.config over
    global_config = pkg_resources.resource_filename(
        'nftest', 'data/global.config'
    )
    test_dir = working_dir/'test'
    test_dir.mkdir(exist_ok=True)
    if not (test_dir/'global.config').exists():
        global_config = shutil.copy2(global_config, test_dir/'global.config')
        print(f'{global_config} created', flush=True)
    else:
        print(f'{test_dir}/global.config already exists', flush=True)

def main():
    """ main entrance """
    args = parse_args()

    if args.version:
        print_version_and_exist()

    args.func(args)

if __name__ == '__main__':
    main()
