# Accessibility labels and large text

- Let Qt expose the current selection summary and status text instead of generic accessible names.
- Wrap the selection summary so larger text does not clip horizontally.
- Add regression coverage for changing accessible text and a 24-point long-summary layout.
- Record limited macOS native accessibility-tree, save/cancel, and Increase contrast checks with synthetic data. VoiceOver speech, keyboard-only export, live system-wide large-text behavior, and distributable release behavior remain unverified; see ACCESSIBILITY.md.
