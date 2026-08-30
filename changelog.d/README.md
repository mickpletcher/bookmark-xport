# Changelog Fragments

[CHANGELOG.md](../CHANGELOG.md) is never edited on a feature branch. Each change adds a fragment here instead, which removes the merge conflicts a single shared changelog generates.

Naming:

```text
changelog.d/2026-08-28-add-chromium-provider.md
```

Contents, using the same headings as the changelog:

```markdown
### Added
- Chrome and Edge bookmark providers backed by a shared Chromium JSON parser.
```

Fragments are concatenated into CHANGELOG.md on merge to main or on a monthly cadence, then deleted.
