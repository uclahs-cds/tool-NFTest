# Changelog

All notable changes to tool-NFTest.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2025-07-01

### Fixed

- Resolve global config relative to `NFT_TESTDIR`

## [1.3.0] - 2025-06-26

### Added

- Allow support for separation of NFTest YAML and test files from pipeline code

## [1.2.1] - 2025-03-06

### Fixed

- Prevent hatch-vcs from picking up major version alias tags

## [1.2.0] - 2024-11-19

### Added

- Add `--report` flag to write out a summary JSON file

### Changed

- Migrate package definition to pyproject.toml

### Fixed

- Properly catch failing test cases

## [1.1.0] - 2024-07-08

### Added

- Validation of reference files

### Changed

- Make `nftest run` exit with the number of failed tests
- Use `shell=False` for subprocess
- Capture Nextflow logs via syslog rather than console
- Format all code with ruff
- Encapsulate NFTestAssert interface, rewrite tests

### Fixed

- Make `nftest` with no arguments print usage and exit
- Resolve non-determinism in NFTestENV unit tests

## [1.0.1] - 2024-01-05

### Fixed

- Path type passed to glob to identify files

## [1.0.0] - 2023-10-23

### Added

- Support for patterns in expected and actual file paths

## [1.0.0-rc.4] - 2023-10-04

### Changed

- Wrap all NextFlow output with real-time line-by-line log statements
- Wrap custom comparison to log through NFTest logger
- Add DEBUG lines about specific asserts
- Assert that actual files are modified by pipelines

### Fixed

- Tests after real-time logging

## [1.0.0-rc.3] - 2023-05-25

### Fixed

- Properly set default value of `clean_logs` according to case and global settings

## [1.0.0-rc.2] - 2023-03-09

### Added

- Case name to output directory path to avoid over-writing
- Support for Nextflow profiles

### Changed

- Override `skip` from configuration YAML for command line test cases

## [1.0.0-rc.1] - 2022-12-01

### Added

- `.env` loading
- Custom directory options
- Logging
- Tests

### Changed

- Document detailed options in `README`

[1.0.0]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.0.0-rc.4...v1.0.0
[1.0.0-rc.1]: https://github.com/uclahs-cds/tool-NFTest/releases/tag/v1.0.0-rc.1
[1.0.0-rc.2]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.0.0-rc.1...v1.0.0-rc.2
[1.0.0-rc.3]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.0.0-rc.2...v1.0.0-rc.3
[1.0.0-rc.4]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.0.0-rc.3...v1.0.0-rc.4
[1.0.1]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.0.0...v1.0.1
[1.1.0]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.0.1...v1.1.0
[1.2.0]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.1.0...v1.2.0
[1.2.1]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.2.0...v1.2.1
[1.3.0]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.2.1...v1.3.0
[1.3.1]: https://github.com/uclahs-cds/tool-NFTest/compare/v1.3.0...v1.3.1
