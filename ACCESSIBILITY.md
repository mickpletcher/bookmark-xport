# Accessibility

## Goal and current status

bookmark-xport aims to support keyboard use and assistive technologies through
native PySide6 / Qt widgets. This is a goal, not a claim of WCAG conformance or
certified screen-reader compatibility.

The current UI in [main_window.py](src/bookmark_exporter/ui/main_window.py) uses
named Browser and Profile controls, a named bookmark folder tree, a selected
folder summary, a status label, and an Export Folder button. Browser, Profile,
and Export Folder have mnemonic labels. Qt provides standard focus navigation
and native save dialogs; behavior depends on the OS, theme, and assistive tool.

Live screen-reader behavior, status announcements, high-contrast themes, and
large-text layouts have not been verified in this accessibility review.
Automated offscreen tests do not establish assistive-technology compatibility.

## Keyboard guidance

- Use Tab and Shift+Tab to move between enabled controls.
- Use arrow keys to navigate combo boxes and the folder tree; use Left and Right
  to collapse and expand tree nodes.
- Select a folder to enable Export Folder, then activate it with the keyboard.
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
