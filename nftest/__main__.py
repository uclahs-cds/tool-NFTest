""" Test NF-pipelines """
from __future__ import annotations
import argparse
import os
import pkg_resources
from pathlib import Path
import shutil
from nftest.common import find_config_yaml, print_version_and_exist
from nftest.NFTestRunner import NFTestRunner


def parse_args() -> argparse.Namespace:
    """ Parse args """
    parser = argparse.ArgumentParser(
        prog='nf-test'
    )
    parser.add_argument(
        '-V', '--version',
        help='Version',
        action='store_true',
        default=False
    )
    parser.add_argument(
        'CONFIG',
        type=Path,
        help='Path the the nextflow test config YAML file. If not given, it'
        ' looks for nf-test.yaml or nf-test.yml',
        default=None,
        nargs='?'
    )
    subparsers = parser.add_subparsers(dest='command')
    add_subparser_init(subparsers)
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

def main():
    """ main entrance """
    args = parse_args()

    if args.version:
        print_version_and_exist()

    if args.command:
        args.func()
        return

    find_config_yaml(args)
    runner = NFTestRunner()
    runner.load_from_config(args.CONFIG)
    runner.main()

def init():
    """ Set up nftest """
    cwd = Path(os.getcwd())

    # copy over the nftest.yaml
    nftest_yaml = pkg_resources.resource_filename(
        'nftest', 'data/nftest.yml'
    )
    if not (cwd/'nftest.yml').exists():
        shutil.copy2(nftest_yaml, cwd)
        print('./nftest.yml  created', flush=True)
    else:
        print('./nftest.yml  already exists', flush=True)

    # copy global.config over
    global_config = pkg_resources.resource_filename(
        'nftest', 'data/global.config'
    )
    test_dir = cwd/'test'
    test_dir.mkdir(exist_ok=True)
    if not (test_dir/'global.config').exists():
        shutil.copy2(global_config, test_dir)
        print('./test/global.config  created', flush=True)
    else:
        print('./test/global.config  already exists', flush=True)

if __name__ == '__main__':
    main()
