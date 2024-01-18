# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.4.2] - 2024-01-18

### Fixed

 - Fix data update when id is retrieved by field key

## [3.4.1] - 2024-01-10

### Changed

 - Update s6r_bitwarden_cli to 1.0.3

## [3.4.0] - 2023-12-27

### Added

 - Allow to retrieve passwords from Bitwarden
 - Allow to type Keepass master password if not provided by env variables or --keepass parameter
 - Allow to get Bitwarden credentials from Keepass. Refactor Keepass functions.

## [3.3.0] - 2023-11-27

### Added

 - Add system_parameter keyword to set ir.config_parameter values
 - Allow to set release_directory and backup release configuration files when release configuration is done

## [3.2.0] - 2023-11-17

### Added

 - Allow to update records in batch with the load function

## [3.1.0] - 2023-07-22

### Added

 - Allow to update records in batch with the load function
 - Allow to set odoo auth params with system environment values
