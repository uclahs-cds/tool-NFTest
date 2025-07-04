# NFTest

[![GitHub release](https://img.shields.io/github/v/release/uclahs-cds/tool-NFTest)](https://github.com/uclahs-cds/tool-NFTest/actions/workflows/prepare-release.yaml)

- [Overview](#overview)
- [Installation](#installation)
    - [From GitHub](#install-directly-from-github)
    - [From local](#install-from-cloned-repository)
- [Badge](#badge)
- [Usage](#usage)
    - [Quickstart](#quickstart)
- [Configuration](#configuration)
    - [Environment settings](#environment-settings)
    - [YAML config](#nftest-yaml-config-file)
        - [Global](#global)
        - [Cases](#cases)
            - [Asserts](#asserts)
- [Development](#development)
    - [Testing](#testing)
- [Discussions](#discussions)
- [Contributors](#contributors)
- [License](#license)

## Overview

Command line tool for automated testing of Nextflow pipelines and scripts. The tool allows for automated assertions on output files and customizable output directory settings.

## Installation
### Install directly from GitHub
```
pip install git+ssh://git@github.com/uclahs-cds/tool-NFTest.git
```
### Install from cloned repository
```
cd </path/to/cloned/repository>
pip install .
```

## Badge
Add the NFTest badge to pipelines:


[![NFTest](https://img.shields.io/badge/Tested%20using-NFTest-green.svg)](https://github.com/uclahs-cds/tool-NFTest)

```
[![NFTest](https://img.shields.io/badge/Tested%20using-NFTest-green.svg)](https://github.com/uclahs-cds/tool-NFTest)
```



## Usage
### Quickstart

1. To initialize the testing framework, run the following in the desired directory:
```
nftest init
```

2. Define the parameters and test cases in the [environment](#environment-settings) and the [config files](#nftest-yaml-config-file).

3. To launch the tests, run:
```
usage: nftest run [-h] [-c [CONFIG_FILE]] [TEST_CASES [TEST_CASES ...]]

Run nextflow tests.

positional arguments:
  TEST_CASES            Exact test case to run. (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -c [CONFIG_FILE], --config-file [CONFIG_FILE]
                        Path the the nextflow test config YAML file. If not given, it looks for nftest.yaml or nftest.yml (default: None)
```
`nftest` expects a config file named `nftest.yaml` or `nftest.yml` in the directory where the command is invoked.

To run all test cases, simply run:
```
nftest run
```


### Initialize

```
usage: nftest init [-h]

Initialize nftest by creating a nftest.yaml template.

optional arguments:
  -h, --help  show this help message and exit
```

Initialization will result in automated creation of a directory for holding test files along with an initial copy of the global configuration file and the test case YAML. These files can subsequently be populated and expanded to define the test cases.

### Run

```
usage: nftest run [-h] [-c [CONFIG_FILE]] [TEST_CASES [TEST_CASES ...]]

Run nextflow tests.

positional arguments:
  TEST_CASES            Exact test case to run. (default: None)

optional arguments:
  -h, --help            show this help message and exit
  -c [CONFIG_FILE], --config-file [CONFIG_FILE]
                        Path the the nextflow test config YAML file. If not given, it looks for nftest.yaml or nftest.yml (default: None)
```
`nftest` expects a config file named `nftest.yaml` or `nftest.yml` in the directory where the command is invoked.

To run all test cases, simply run:
```
nftest run
```

To run specific test case(s), use the following command
 
 ```
 nftest run <test name in nftest.yaml file>
 ```

## Configuration
### Environment settings
Testing runs can be configured through environment variables. Theses variables can be stored in `~/.env` or `<current working directory>/.env` in `dotenv` format. See [template](.env-template) for an example. Alternatively, the variables can also be set through `export` (for `Bash` and `zsh` shells) in the shell prior to running the tool. The available environment variable settings are:

|Variable|Description|Default|
|:--:|:--:|:--:|
|`NFT_OUTPUT`|Output directory for parameter for Nextflow. Parameter name is designated by `output_directory_param_name` for each case.|Current working directory|
|`NFT_TEMP`|Temporary directory root to be used for Nextflow working files. Combined with `temp_dir` from global configuration to create final directory. See `NXF_WORK` [here](https://www.nextflow.io/docs/latest/config.html#environment-variables) for details.|Current working directory|
|`NFT_INIT`|Directory where initialized files will be created. Also the directory where the tool will search for the global configuration file.|Current working directory|
|`NFT_LOG_LEVEL`|Python `logging` level. See [logging levels](https://docs.python.org/3/library/logging.html#logging-levels) for more details and available options.|`INFO`|
|`NFT_LOG`|Path to file for writing log messages. By default, logging will append to file if it exists.|`<NFT_OUTPUT>/log-nftest-<date>.log`|
|`NFT_PIPELINE`|Path to directory containing Nextflow script to run.|Value of `NFT_INIT`|
|`NFT_TESTDIR`|Path to directory containing test files for test cases.|Directory containing the config YAML (nftest.yaml)|

### `nftest` YAML config file

The YAML config file outlining the test cases is required to have two keys at the top level: `global` and `cases`. The `global` key controls global settings such as the path to the Nextflow temporary directory, global Nextflow config, and whether to remove Nextflow temporary files are each test case. The `cases` key contains the list of test cases. See [here]

The config file requires to have two keys at the top level, `global` and `cases`. `global` controls global settings such as path to the nextflow temporary dir, global nextflow config, whether to remove nextflow temporary files after each run. `cases` holds a list of all test cases. See [here](https://github.com/uclahs-cds/pipeline-germline-somatic/blob/af5e984a247a241f7b4cfbb7af97e0bf1640e7e6/nf-test.yaml) for an example.

#### Global
The settings available with the `global` key:

|Setting|Description|Default|
|:--:|:--:|:--:|
|`temp_dir`|Directory to be added to `NFT_TEMP` environment variable to create Nextflow working directory.|_required_|
|`nf_config`|Path to be added to `NFT_INIT` to derive global `.config` file for Nextflow.|_required_|
|`remove_temp`|Whether to remove the Nextflow working directory after each case.|`True`|
|`clean_logs`|Whether to remove log files generated by Nextflow.|`True`|

#### Cases
The list of cases and settings for each case. The settings from [global](#global) will be used for each case as default if specific settings for a case are not provided.

The settings available for each case:

|Setting|Description|Default|
|:--:|:--:|:--:|
|`temp_dir`|Directory to be added to `NFT_TEMP` environment variable to create Nextflow working directory.|_value from global_|
|`nf_config`|Path to be added to `NFT_INIT` to derive global `.config` file for Nextflow.|_value from global_|
|`profiles`|Ordered list of profiles to use with Nextflow through the `-profile` option.|`None`|
|`remove_temp`|Whether to remove the Nextflow working directory after each case.|_value from global_|
|`clean_logs`|Whether to remove log files generated by Nextflow.|_value from global_|
|`name`|Name of the test case; used to identify the case and for selecting specific cases to run.|`None`|
|`message`|Message to display in log when running test case.|`None`|
|`nf_script`|Nextflow script to run for test case.|`None`|
|`nf_configs`|List of config file(s) to be passed to Nextflow via the `-c` option for `nextflow run`.|`[]`|
|`params_file`|`JSON` or `YAML` file containing parameters for Nextflow script.|`None`|
|`output_directory_param_name`|Parameter name to pass output directory to Nextflow. Passed through command line.|`output_dir`|
|`asserts`|List of assertions to make for test case. See [assertions](#asserts) for details.|`[]`|
|`skip`|Whether to skip this test case.|`False`|
|`verbose`|Whether to capture output of `nextflow run` command in log.|`False`|

##### Asserts
Asserts define a list of assertions to be made for each given test case. For each case, the tool checks if a `script` for comparison was provided. If provided, it gets used; otherwise, the tool checks for the `method`. The available methods are: `md5` checksum comparison.

Settings available for each assert:

|Setting|Description|Default|
|:--:|:--:|:--:|
|`actual`|Path to be added to `NFT_OUTPUT` to derive output file to be checked by this assertion.|_required_|
|`expect`|Path to expected output file for comparison to `actual`.|_required_|
|`method`|Comparison method to be used for comparing files. Available: `md5`|`md5`|
|`script`|Custom comparison script that can be run from the command line with 2 positional arguments: `actual` and then `expect`. Script must return an exit code of `0` for success and anything else for failure.|`None`|

## Development
### Testing
Testing for NFTest itself can be done through `pytest` by running the following:
```
pytest
```
in the root of the repository directory.

## Discussions

- [Issue tracker](https://github.com/uclahs-cds/tool-NFTest/issues) to report errors and enhancement ideas.
- Discussions can take place in [tool-NFTest Discussions](https://github.com/uclahs-cds/tool-NFTest/discussions)
- [tool-NFTest pull requests](https://github.com/uclahs-cds/tool-NFTest/pulls) are also open for discussion

---

## Contributors

Please see list of [Contributors](https://github.com/uclahs-cds/tool-NFTest/graphs/contributors) at GitHub.

---

## License
Author: Yash Patel, Chenghao Zhu, Helena Winata

NFTest is licensed under the GNU General Public License version 2. See the file LICENSE for the terms of the GNU GPL license.

NFTest is a tool for automating Nextflow pipeline testing.

Copyright (C) 2021-2023 University of California Los Angeles ("Boutros Lab") All rights reserved.

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
