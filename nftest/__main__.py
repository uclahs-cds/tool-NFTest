""" Test NF-pipelines """
from __future__ import annotations
import argparse
from pathlib import Path
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
    return parser.parse_args()

def main():
    """ main entrance """
    args = parse_args()
    if args.version:
        print_version_and_exist()
    find_config_yaml(args)
    runner = NFTestRunner()
    runner.load_from_config(args.CONFIG)
    runner.main()


if __name__ == '__main__':
    main()
