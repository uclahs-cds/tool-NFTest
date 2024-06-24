# Changelog
All notable changes to tool-NFTest.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Added
- Validation of reference files

### Changed
- Make `nftest run` exit with the number of failed tests
- Use `shell=False` for subprocess
- Capture Nextflow logs via syslog rather than console
- Format all code with ruff

### Fixed
- Make `nftest` with no arguments print usage and exit
- Resolve non-determinism in NFTestENV unit tests

---

## [1.0.1] - 2024-01-05
### Fixed
- Path type passed to glob to identify files

---

## [1.0.0] - 2023-10-23
### Added
- Support for patterns in expected and actual file paths

---

## [1.0.0-rc.4] - 2023-10-04
### Changed
- Wrap all NextFlow output with real-time line-by-line log statements
- Wrap custom comparison to log through NFTest logger
- Add DEBUG lines about specific asserts
- Assert that actual files are modified by pipelines

### Fixed
- Tests after real-time logging

---

## [1.0.0-rc.3] - 2023-05-25
### Fixed
- Properly set default value of `clean_logs` according to case and global settings

---

## [1.0.0-rc.2] - 2023-03-09
### Added
- Case name to output directory path to avoid over-writing
- Support for Nextflow profiles
### Changed
- Override `skip` from configuration YAML for command line test cases

---

## [1.0.0-rc.1] - 2022-12-01
### Added
- `.env` loading
- Custom directory options
- Logging
- Tests
### Changed
- Document detailed options in `README`
