# Future Upgrades

Deferred improvements. Implemented upgrades move to [docs/archive/COMPLETED-UPGRADES.md](docs/archive/COMPLETED-UPGRADES.md) and are removed from this file.

### FU-001 — Additional Chromium browser providers

**Status:** Proposed
**Priority:** Medium
**Area:** Browser providers
**Origin:** Internal — named as future scope in [prompts/COPILOT-BUILD-PROMPT.md](prompts/COPILOT-BUILD-PROMPT.md)

**Opportunity**
Add Brave, Vivaldi, Opera, Arc, and plain Chromium as providers.

**Potential benefit**
Broader coverage at low marginal cost, since these browsers use the same JSON bookmark store as Chrome and Edge. Most of the work is path and profile discovery.

**Why deferred**
The initial four browsers must prove the provider interface first. Adding providers before the interface is stable multiplies the cost of changing it.

**Trigger**
The Chromium parser is shared cleanly between Chrome and Edge with no duplication, and the provider interface has survived the Firefox and Safari implementations without modification.

**Estimated effort:** Small per browser
**Dependencies:** Stable `BrowserProvider` interface and a reusable Chromium parser.

---

### FU-002 — Command-line export mode

**Status:** Proposed
**Priority:** Low
**Area:** Application entry points
**Origin:** Internal

**Opportunity**
A non-GUI entry point that takes a browser, profile, folder path, and output path, and writes the HTML file without user interaction.

**Potential benefit**
Makes the tool scriptable and schedulable, and makes integration testing far easier than driving a Qt interface.

**Why deferred**
The GUI is the stated product goal. A CLI added before the service layer is stable would couple to a moving target.

**Trigger**
The export service is callable without any Qt import, which is the same separation the architecture already requires.

**Estimated effort:** Small
**Dependencies:** Export service fully decoupled from the UI layer.

---

## Entry Template

```markdown
### FU-00X — Short Title

**Status:** Proposed | Planned | In Progress | Rejected
**Priority:** Low | Medium | High
**Area:** Component or concern
**Origin:** Internal

**Opportunity**
**Potential benefit**
**Why deferred**
**Trigger**
**Estimated effort:** Small | Medium | Large
**Dependencies**
```
