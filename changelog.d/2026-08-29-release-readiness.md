### Added

- Added pytest-qt interaction coverage, privacy regression tests, branch coverage, Ruff, strict mypy, CodeQL, Dependabot, locked development dependencies, and Windows and macOS package smoke jobs.
- Added a reproducible bundle smoke test and public security reporting policy.

### Changed

- Preserved mixed bookmark and subfolder ordering in the normalized model and HTML export.
- Made export writes atomic and removed bookmark content from successful export logs.
- Updated URL redaction so credentials, paths, queries, and fragments cannot enter logs.
- Expanded CI to Windows, macOS, and Ubuntu on Python 3.12 and 3.13 using current Node 24 based GitHub Actions.
- Moved the repository from Greenfield to Maintenance lifecycle mode and synchronized living documentation.

### Fixed

- Fixed initial discovery failing to load the first usable browser when the combo box index changed while signals were blocked.
- Fixed the build wrapper so direct virtual-environment Python invocation finds its own PyInstaller module.
- Fixed stale tracking documents and removed tracked machine-name conflict copies.
