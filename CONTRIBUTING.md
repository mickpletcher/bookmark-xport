# Contributing to bookmark-xport

Thank you for helping make single-folder bookmark export useful and accessible.
Follow the [Code of Conduct](CODE_OF_CONDUCT.md) in all project spaces.

## Before you start

Read [AGENTS.md](AGENTS.md) and [PROJECT-STANDARD.md](PROJECT-STANDARD.md).
Those files remain the authority for development and documentation rules.
Use the [README setup instructions](README.md#getting-started) to install the
locked dependencies and editable package. Python 3.12 or later is required.

Search existing [issues](https://github.com/mickpletcher/bookmark-xport/issues)
and [pull requests](https://github.com/mickpletcher/bookmark-xport/pulls) before
starting work. Use an issue template for bugs, enhancements, or accessibility
barriers. Confirmed defects are tracked in [ISSUES.md](ISSUES.md); GitHub issues
are the public intake, not a second authoritative defect register.

## Privacy and safety

- Browser data must remain read-only. Never automate a browser UI to obtain it.
- Use synthetic fixtures only. Never upload real bookmarks, browser databases,
  exports, profile paths, credentials, or screenshots containing private data.
- Follow [SECURITY.md](SECURITY.md) for vulnerability reports instead of public issues.

## Submit a change

1. Create a focused branch from `main`.
2. Add or update tests for changed behavior and follow the
   [accessibility guidance](ACCESSIBILITY.md) for UI changes.
3. Run the commands in [README validation](README.md#validation). For UI tests,
   set `QT_QPA_PLATFORM=offscreen` when no display is available.
4. Add a meaningful change fragment under `changelog.d/`. Do not edit
   `CHANGELOG.md` or `ASSESSMENT.md` on a feature branch.
5. Update the routed documentation in the same change. Record commands, exit
   codes, passed/skipped counts, and any environmental limitation honestly.
6. Open a pull request with the supplied checklist. Address review feedback and
   wait for the required checks. Maintainers squash-merge accepted changes.

Do not weaken tests, disable protections, or claim an unperformed accessibility
or platform check passed. See [VALIDATION.md](VALIDATION.md) for release gates.
