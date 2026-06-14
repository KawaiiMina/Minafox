# MinaFox sprint — Cosmic start page MVP

## Goal
Implement the next MinaFox sprint by making the local `desktop/start.html` substantially closer to the Cosmic Arc/Zen mockup while preserving the package/standalone/SearXNG work already completed.

## Current context
- Repo: `/home/hermes/Minafox`
- Latest completed sprint: packaged local SearXNG user service (`09d418f`).
- Existing UI validator passes, but it only checks the older simple start page classes.
- The saved Cosmic Arc UI plan already defines Phase 1 as the next visual sprint.

## Scope for this sprint
Focus on Phase 1: start page mockup MVP.

### Files likely to change
- `desktop/start.html`
- `scripts/validate-minafox-ui.py`
- `README.md`

## Implementation steps
1. TDD RED: extend `scripts/validate-minafox-ui.py` to require the new mockup structure:
   - `minafox-desktop`
   - `workspace-rail`
   - `soft-tabs`
   - `soft-tab-list`
   - `command-bar`
   - `dashboard-grid`
   - `widget-grid`
   - `focus-timer-card`
   - `notes-card`
   - `lofi-card`
   - `roadmap-card`
   - `design-system-card`
   Then run `python3 scripts/validate-minafox-ui.py` and confirm it fails for missing classes.
2. Implement `desktop/start.html` as a mockup-like static local dashboard:
   - floating left workspace rail
   - soft tab/workspace pills
   - centered command/search bar preserving `method="post"`, `action="http://127.0.0.1:8888/search"`, and `input name="q"`
   - greeting, quick app cards, focus timer, notes, lofi, roadmap/Gantt, design-system card
   - responsive layout below tablet/mobile widths
   - visible `:focus-visible` states and `prefers-reduced-motion`
3. Update README’s Hybrid MinaFox UI section to describe the richer start page.
4. Run validation gates:
   - `python3 scripts/validate-minafox-ui.py`
   - `python3 scripts/validate-minafox-standalone.py`
   - `python3 scripts/validate-minafox-arch-package.py`
   - `python3 scripts/validate-no-host-paths.py`
   - `python3 scripts/validate-no-firefox-telemetry.py`
   - `python3 scripts/validate-minafox-searxng.py`
   - `bash -n scripts/install-minafox-arch.sh scripts/install-minafox-searxng-arch.sh scripts/minafox-launcher.sh`
   - `python3 -m py_compile scripts/validate-minafox-ui.py`
   - `git diff --check`
5. Independent review the resulting diff for security and logic issues.
6. Fix reviewer issues if any, re-run gates, then commit locally.

## Acceptance criteria
- Validator demonstrates RED before production HTML changes.
- Final UI validator passes with the new required structure.
- Search still posts to local SearXNG on `127.0.0.1:8888/search`.
- Existing quick links are preserved.
- No host paths or placeholders regressions.
- Package/standalone/SearXNG validators still pass.
- Commit locally with a concise sprint commit message.

## Manual Firefox notes
A full graphical Firefox/DevTools visual check may be blocked in this headless environment. If so, report that honestly and rely on deterministic HTML/CSS validators plus shell smoke checks for this sprint.