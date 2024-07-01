# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.5.0] - 2024-06-27

### Changed

 - Users configuration

### Added 

 - JSON field type:
    ```yml
       field_name/json: [{'key': 'value'}]
    ```
 - Context parameter in import yml file
 - Load optimization
 - XMLID cache optimization

## [3.4.11] - 2024-06-17

### Added 

 - Using many2many fields in export record prefix

## [3.4.10] - 2024-06-11

### Added 

 - Compatibility with Odoo 17.0

## [3.4.9] - 2024-06-05

### Fixed 

 - Improve update of many2many list of xmlid when the record has no xml_id
 - Improve update of Many2one field with a xmlid when the record has no xml_id

## [3.4.8] - 2024-05-23

### Added

 - Allows to import many2many field values with xml_id

### Fixed

 - Improve get_local_file function to avoid to set working directory environment variable 

## [3.4.7] - 2024-05-02

### Added

 - Add get_bitwarden_username and get_bitwarden_field functions


## [3.4.6] - 2024-04-12

### Fixed

 - add allowed_company_ids in context to properly config accounting fields such chart_template_id on res.config.setting
 - update_domain function can be used with several conditions in domain


## [3.4.5] - 2024-03-14

### Added

 - Compute missing xmlid on export

## [3.4.4] - 2024-02-07

### Added

 - Allows multi-company configuration
 - add a context parameter in config

## [3.4.3] - 2024-01-23

### Added

 - Handle Bitwarden two-step login code

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
