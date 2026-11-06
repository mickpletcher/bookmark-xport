# Accessibility

## Goal and current status

bookmark-xport aims to support keyboard use and assistive technologies through
native PySide6 / Qt widgets. This is a goal, not a claim of WCAG conformance or
certified screen-reader compatibility.

The current UI in [main_window.py](src/bookmark_exporter/ui/main_window.py) uses
named Browser and Profile controls, a named bookmark folder tree, a selected
folder summary, a status label, and an Export Folder button. Summary and status
labels expose their current text through Qt's accessibility interface, and the
summary wraps to accommodate larger text. Browser, Profile,
and Export Folder have mnemonic labels. Qt provides standard focus navigation
and native save dialogs; behavior depends on the OS, theme, and assistive tool.

Live checks have verified native accessibility text and macOS Increase contrast
in the limited setup described below. VoiceOver speech and status announcements
remain unverified. Automated offscreen tests do not establish assistive-technology
compatibility.

## Verified scope and remaining limits

On 2026-11-06, a source-driven test launcher was exercised on macOS 26.7.1
with Python 3.13.18 and PySide6 6.11.2. It used main commit `419d871` plus
the accessible-label and summary-wrapping fixes, with an isolated synthetic
browser provider. No real browser bookmark data was needed.

- The native UI and accessibility tree exposed the actual selected-folder summary
  and export-complete text. This verifies available text, not spoken announcements.
- Escape canceled the save dialog and returned to a usable application window.
  Opening it again and saving produced the expected synthetic HTML with an
  `example.test` bookmark and nested folder.
- With macOS **Increase contrast** enabled, controls, text, selection, and summary
  remained readable. Increase contrast was restored to off afterward.
  **Reduce transparency** remained on throughout. This is a check of that
  configuration, not every macOS appearance setting or Windows high-contrast mode.
- Keyboard-only export is not verified. With the application raised, Tab,
  Shift+Tab, and Option+Tab did not move focus from the folder tree to Export
  Folder; Enter did not open the save dialog. Earlier Space/Return attempts
  also did not open it; clicking Export Folder did. The macOS setting
  **Use keyboard navigation to move focus between controls** was confirmed off,
  which explains Tab skipping the button. It was left unchanged. These results
  do not establish an application keyboard defect; retest with keyboard navigation
  enabled before claiming the complete keyboard-only flow works.
- With explicit permission, VoiceOver was enabled through System Settings and its
  first-run **Use VoiceOver** dialog completed. The VoiceOver process was observed
  running. However, attempts to inspect its caption/output window repeatedly timed
  out, and VoiceOver navigation keys produced no observable cursor change.
  Speech, announcements, and VoiceOver navigation therefore remain unverified due
  to observation/control limitations, not missing authorization. VoiceOver was
  restored to off, with both the disabled setting and absence of its process
  confirmed. Native accessibility-tree inspection is not a substitute for these
  live screen-reader checks.
- Offscreen regression tests verify changing Qt accessible text and a wrapped
  24-point long summary. A live system-wide large-text layout check is still pending.

The Mac's full test suite, including the three new regression cases, passed:
96 passed, one Windows-only LOCALAPPDATA test skipped, and 85.49% coverage.
Ruff lint and formatting, mypy (37 files), `pip check`, and `git diff --check`
also passed. In the Linux cloud checkout, the same regression cases and suite
produced 96 passed, one Windows-only skip, and 86.24% coverage; Ruff, formatting,
mypy, and `pip check` passed.

This was a source-driven launcher, not a verified distributable release.
A test-launcher packaging attempt was blocked by the Xcode license requirement
(`lipo` exit 69); a simple local shell application launcher was used for native
UI checks instead. Packaged release behavior is not established by these results.

## Keyboard guidance

- Use Tab and Shift+Tab to move between enabled controls.
- Use arrow keys to navigate combo boxes and the folder tree; use Left and Right
  to collapse and expand tree nodes.
- Select a folder to enable Export Folder. Keyboard activation remains unverified
  on the tested Mac; see the limitation above.
- Cancel the save dialog to return without exporting.
- Mnemonics are exposed by Qt according to the platform's keyboard conventions.

If this does not work with your setup, please report the barrier below.

## Contributor checklist

For UI changes, check with synthetic data:

- Every interactive control has a meaningful accessible name and visible label.
- Focus order is logical, focus is visible, and no keyboard trap exists.
- Selecting and exporting a folder works without a mouse.
- Canceling a dialog restores a usable window and does not export a file.
- Errors and busy/completed states are understandable without color alone.
- Content remains usable with larger system text and high-contrast settings.
- A supported screen reader can identify controls, selected folders, and status
  changes. Record the OS, screen reader/version, and actual results.

Use [VALIDATION.md](VALIDATION.md) for the general validation process. Record
untested manual checks as limitations rather than marking them passed.

## Report a barrier

Open an [accessibility report](https://github.com/mickpletcher/bookmark-xport/issues/new?template=accessibility.md).
Include the OS, application version or commit, assistive technology if relevant,
steps, expected behavior, and what happened. Do not include real bookmark
content, profile paths, or private screenshots. A synthetic example is enough.
