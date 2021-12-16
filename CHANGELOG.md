# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased] - yyyy-mm-dd

## Added

- Added ability to upload files to cloud
  - [anonfiles](https://anonfiles.com/)
  - [gofiles](https://gofile.io/)

## Changed

- lxml 4.6.4 -> 4.6.5

## [0.8.1] - 2021-12-13

## Changed

- Removed url lazy loading from db in favour of sql statement
- Changed discord session `call` to `get` and it now returns the method
  instead of calling it

## Fixed

- Fixed where provided webnovel urls not added to db #44
- Fixed discord dm message
- Fixed discord thread access errors

## [0.8.0] - 2021-11-25

### Added

- Added github issue templates
- Added CHANGELOG.md
- Added `--json` output option for info command
- Added pre-commit checks for consistent style
- Added pre-commit badge to README.md
- Added change log to database migrations README.md
- Added discord bot with (most functions are only available in private):
  - Download novel to multiple formats
  - Search for novels using a query
- Added alternative method to acquire package version if importlib fails

### Changed

- Updated project dependencies
- Changed logging style
- Changed novel list to display as a table
- Renamed novelsave/static to novelsave/resources

### Fixed

- Fix empty dict-value error in inject_assets

## [0.7.8] - 2021-11-03

### Added

- Added text packager
- Added `--skip-updates` flag
- CODE_OF_CONDUCT.md
- CONTRIBUTING.md
- Config: Version 2

### Changed

- Lifted migrations from empty folder infrastructure
- No longer modify the provided urls

### Fixed

- Fixed tests
- Fix: skip updates not working as intended
- Fix empty dict-value error in inject_assets

## [0.7.7] - 2021-10-03

### Added

- Added `--target-all` to process command (was previously omitted).

### Changed

- Transitioned build to poetry.
- Transitioned source parser to the new interface
- Output is no longer bold in info level

### Fixed

- Fix where an error was raised when threads was None.

## [0.7.6] - 2021-09-22

### Added

- Added mobi packager
- Added pdf packager
- Added azw3 packager
- Added `--target-all` argument to packaging
- Added packaging priority

### Changed

- Raise error if packaging keyword not recognized
- Don't check for updates if this it is a help call
- Moved more options to setup.cfg

## [0.7.5] - 2021-09-20

### Fixed

- Moved `static` package into `novelsave` since, it was not being packaged.

## [0.7.4] - 2021-09-20

### Added

- Added packaging target: `html`

### Changed

- Disable update check when using --help
- Expanded info command to show more detials

### Fixed

- Fixed log file encoding error

## [0.7.3] - 2021-09-10

### Added

- Support for `novelsave_sources` v0.2.0

### Changed

- Switched to built-in concurrent module

## [0.7.2] - 2021-09-01

### Fixed

- Fix novelsave-sources==0.1.1 import error

## [0.7.1] - 2021-09-01

### Added

- Auto check for updates at end of program execution.
- New command `list` that would show all the novels in database.
- Handle connection error during updating and remind to check for internet connection.

### Changed

- All novel urls must now end in slash `/` and will be adjusted appropriately.
- Show logging level label if its not info `DEBUG: ...` `ERROR: ...`
- Logger now keeps an individual log file for each run that is compressed at end.
- Some adjustments to log console output.

## [0.7.0] - 2021-08-28

Due to the extreme change in code it is recommended that you explicitly uninstall the existing version

```bash
pip uninstall novelsave
```

and force reinstall novelsave and its dependencies (otherwise dependencies might not upgrade)

```bash
pip install novelsave --force
```

### Added

- Image downloading and embedding
- Multiple urls per novel

### Changed

- Changed database into sql via sqlalchemy and alembic
- Major changes to command-line interface
