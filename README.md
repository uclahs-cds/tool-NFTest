# nftest

Command line tool for automated testing of Nextflow pipelines.

## Install

```
pip install git+ssh://git@github.com:uclahs-cds/tool-NF-test.git
```

## Usage

nftest expects a config file names 'nftest.yaml' or 'nftest.yml' at the root directory of the nextflow pipelien repo. Run the simple command to launch test cases.

```
nftest
```

## Config file

The config file reuires to have two keys at the top level, `global` and `cases`. `global` controls global settings such as path to the nextflow temporary dir, global nextflow config, whether to remove nextflow temporary files after each run. `cases` holds a list of all test cases. See [here](https://github.com/uclahs-cds/pipeline-germline-somatic/blob/af5e984a247a241f7b4cfbb7af97e0bf1640e7e6/nf-test.yaml) for an example.