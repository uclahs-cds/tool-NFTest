# NFTest

Command line tool for automated testing of Nextflow pipelines.

## Installation
### Install directly from GitHub
```
pip install git+ssh://git@github.com/uclahs-cds/tool-NF-test.git
```
### Install from cloned repository
```
cd </path/to/cloned/repository>
pip install .
```

## Usage

`nftest` expects a config file named `nftest.yaml` or `nftest.yml` in the directory where the command is invoked.

To run all test cases, simply run:
```
nftest run
```

To run specific test case(s), use the following command
 
 ```
 nftest run <test name in nftest.yaml file>
 ```

## `nftest` YAML config file

The YAML config file outlining the test cases is required to have two keys at the top level: `global` and `cases`. The `global` key controls global settings such as the path to the Nextflow temporary directory, global Nextflow config, and whether to remove Nextflow temporary files are each test case. The `cases` key contains the list of test cases. See [here]

The config file requires to have two keys at the top level, `global` and `cases`. `global` controls global settings such as path to the nextflow temporary dir, global nextflow config, whether to remove nextflow temporary files after each run. `cases` holds a list of all test cases. See [here](https://github.com/uclahs-cds/pipeline-germline-somatic/blob/af5e984a247a241f7b4cfbb7af97e0bf1640e7e6/nf-test.yaml) for an example.
