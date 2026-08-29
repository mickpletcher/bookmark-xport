# bookmark-xport — Project Build Itinerary

Source of truth for scope/architecture: `prompts/COPILOT-BUILD-PROMPT.md`.
This itinerary sequences that spec into concrete phases with entry/exit
criteria, folds in the outstanding items from the repo audit, and applies
your standard living-docs setup (CHANGELOG.md, ASSESSMENT.md,
FUTURE-UPGRADES.md, COMPLETED-UPGRADES.md).

Status key: `[ ]` not started · `[~]` in progress · `[x]` done

---

## Phase 0 — Repo & Project Hygiene (before any code)

Do this first — it's cheap now and expensive to retrofit once source exists.

- [x] `prompts/readme.md` placeholder content fixed
- [x] `.gitignore` extended (real bookmark/profile DB guard added)
- [x] `SECURITY.md` added
- [ ] Apply `bookmark-xport-hygiene-fixes.patch` to `main` (I couldn't push it — no repo credentials)
- [ ] Choose and add `LICENSE` (MIT is the common default for a personal utility tool — confirm)
- [ ] Add `CHANGELOG.md`, `ASSESSMENT.md`, `FUTURE-UPGRADES.md`, `COMPLETED-UPGRADES.md` at repo root, per your standard project template
- [ ] Add topics on GitHub: `python`, `pyside6`, `bookmarks`, `chrome`, `firefox`, `edge`, `safari`, `desktop-app`
- [ ] Enable Dependabot alerts + security updates, secret scanning + push protection, private vulnerability reporting (Settings → Code security)
- [ ] Add `CODEOWNERS` (`* @mickpletcher`) — needed before branch protection can require reviews
- [ ] Set branch protection on `main`: require PRs, block force-push/deletion; hold off on required status checks and "include administrators" until Phase 1 CI exists

**Exit criteria:** repo has a license, the four living docs exist (even if mostly empty scaffolding), and baseline GitHub security features are on.

---

## Phase 1 — Foundation

From the spec: project structure, package config, normalized models, provider interface, logging, tests scaffold.

- [ ] Create `src/bookmark_exporter/` package layout from the spec's suggested structure
- [ ] `pyproject.toml` + `requirements.txt` (Python 3.12+, PySide6, pytest, PyInstaller — stdlib preferred otherwise)
- [ ] Normalized models: `Bookmark`, `BookmarkFolder` (`models/bookmarks.py`)
- [ ] `BrowserProvider` abstract interface (`browsers/base.py`)
- [ ] Logging setup — no full URLs at normal log levels, no bookmark contents in crash reports (privacy requirement from spec)
- [ ] `tests/` scaffold + `tests/fixtures/` (sanitized fixtures only, never a real profile)
- [ ] `.github/workflows/tests.yml` — run pytest on push/PR
- [ ] Now enable required status checks on `main` branch protection (CI exists)
- [ ] Add `.github/dependabot.yml` for pip version updates now that `requirements.txt` exists

**Exit criteria:** `pytest` runs green with placeholder/interface-level tests; CI is green on a PR; nothing browser-specific implemented yet.

---

## Phase 2 — Chrome End-to-End Proof of Concept

The first real, demonstrable workflow.

- [ ] `browsers/chromium.py` — reusable Chromium JSON `Bookmarks` file parser
- [ ] `browsers/chrome.py` — Chrome path/profile discovery (multi-profile: `Default`, `Profile 1`, …)
- [ ] Parse bookmark bar, other bookmarks, other valid roots; handle missing/optional keys safely
- [ ] `exporters/html_exporter.py` — Netscape Bookmark File Format output, HTML-escaped, nested folders preserved
- [ ] `services/export_service.py` wiring provider → model → exporter
- [ ] Minimal UI (even a bare PySide6 window is fine here) or CLI-style manual test harness: select Chrome → profile → folder → export
- [ ] `services/browser_discovery.py` distinguishes: data available / installed-but-unavailable / unsupported OS / permission denied
- [ ] Unit tests: single/nested/empty folders, multiple profiles, malformed JSON, Unicode
- [ ] Manually validate exported HTML imports cleanly into Chrome, Edge, and Firefox

**Exit criteria:** Definition-of-done bullet from the spec — "Chrome works end-to-end" — is true and demonstrable.

---

## Phase 3 — Edge

- [ ] `browsers/edge.py` reusing the Chromium parser from Phase 2 — no duplicated parsing logic
- [ ] Edge-specific path/profile discovery
- [ ] Tests mirroring Phase 2's Chromium coverage
- [ ] Validate exported HTML imports into Chrome, Edge, Firefox

**Exit criteria:** Edge and Chrome both work end-to-end through the same Chromium provider code path.

---

## Phase 4 — Firefox

- [ ] `browsers/firefox.py` — profile discovery + `places.sqlite` extraction
- [ ] Read-only access; safe temporary-copy strategy if the DB is locked (Firefox running)
- [ ] Correctly reconstruct hierarchy/ordering; never confuse history with bookmarks
- [ ] `tests/test_firefox.py` — hierarchy, ordering, multiple profiles, read-only behavior, locked-DB handling
- [ ] Validate exported HTML from a Firefox source imports cleanly elsewhere

**Exit criteria:** Firefox works end-to-end and never writes to the live profile, even when Firefox is running.

---

## Phase 5 — Safari (macOS only)

- [ ] `browsers/safari.py` — safest reliable extraction method for current macOS
- [ ] Detect and clearly report Full Disk Access / permission restrictions rather than crashing
- [ ] Gracefully report "unsupported on this OS" on Windows/Linux
- [ ] `tests/test_safari.py` — fixture parsing where practical, unsupported-OS path, permission-denied path

**Exit criteria:** Safari works on supported macOS, or fails with an actionable message everywhere else — never a crash.

---

## Phase 6 — UX Hardening

- [ ] Loading states while profiles/bookmarks load (UI stays responsive)
- [ ] Concise, actionable error surfaces; technical detail routed to logs only
- [ ] Folder tree: selected-folder summary (bookmark count, subfolder count)
- [ ] Remember last export directory (without storing bookmark contents)
- [ ] Sanitized default export filename (Windows/macOS-safe), e.g. `Development-Bookmarks.html`
- [ ] Accessibility pass: keyboard navigation, labels, non-mouse workflows where practical

**Exit criteria:** the app is comfortable to use start-to-finish, not just functionally correct.

---

## Phase 7 — Testing & Packaging

- [ ] Full test suite covering: Chromium (single/nested/empty/multi-profile/malformed JSON/Unicode), Firefox (hierarchy/order/multi-profile/read-only), Safari (fixture + unsupported-OS + permission paths), HTML export (nesting/escaping/Unicode/unusual URLs/empty folders/deterministic output)
- [ ] `scripts/build.py` — PyInstaller builds for Windows and macOS, packaging logic kept separate from app logic
- [ ] Project still runs directly from source (packaging is additive, not required to run)
- [ ] Tag a `v0.1.0` release once Definition of Done is met; publish under Releases

**Exit criteria — full Definition of Done from the spec:**
Chrome/Edge/Firefox work end-to-end; Safari works or fails safely; multi-profile works; folder trees are browsable; exactly one folder exports at a time with nesting preserved; exported HTML round-trips through Chrome/Edge/Firefox; browser data is never modified; errors never crash the app; automated tests pass; README/CHANGELOG/ASSESSMENT/FUTURE-UPGRADES reflect current state; app runs from source and packages via PyInstaller.

---

## Ongoing, every phase (per your standard + the spec's own workflow section)

- Update `CHANGELOG.md` with every meaningful change
- Update `ASSESSMENT.md` after every change — current-state snapshot, honest about gaps
- Move completed items from `FUTURE-UPGRADES.md` to `COMPLETED-UPGRADES.md` as they land, backfilling `FUTURE-UPGRADES.md` with newly identified ideas
- Review `README.md` whenever a change affects setup, usage, capabilities, or supported platforms
- Work in small PRs into `main` (branch protection from Phase 0 enforces this); run tests/lint before each PR
- Never commit real bookmark databases, real profile paths, or build artifacts

## Explicitly deferred (per the spec — track in `FUTURE-UPGRADES.md`, don't build now)

Import selected folders · export multiple folders · search · duplicate detection ·
broken-link checking · JSON/CSV export · browser-to-browser comparison/copy ·
scheduled backups · CLI · portable mode · more Chromium-based browsers (Brave,
Vivaldi, Opera, Arc) · signed installers · automatic updates.
