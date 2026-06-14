# MinaFox sprint — Chrome command-bar polish

## Goal
Implement the next MinaFox Cosmic Arc UI sprint: make the Firefox chrome layer (`userChrome.css`) closer to the mockup with a centered command-bar URL bar, softer glass toolbar surfaces, stronger pink/violet active tab pills, and sidebar/panel styling that remains conservative and maintainable.

## Current context
- Repo: `/home/hermes/Minafox`
- Latest completed sprint: Cosmic Arc / Zen start page MVP (`58b9eb2`).
- The broader Cosmic UI plan marks Phase 2 as the next step after the start page MVP.
- This is profile CSS over system Firefox, not a source fork; selectors must stay conservative.

## Scope for this sprint
Focus on Phase 2: browser chrome closer to the mockup.

### Files likely to change
- `profile/userChrome.css`
- `profile/userContent.css` only if scoped content support needs small polish
- `scripts/validate-minafox-ui.py`
- `README.md`

## Implementation steps
1. TDD RED: extend `scripts/validate-minafox-ui.py` so `profile/userChrome.css` must include the new Phase 2 chrome tokens/selectors:
   - `--mf-command-glow`
   - `--mf-rail-bg`
   - `--mf-pill-active`
   - `#urlbar-container`
   - `#urlbar[focused="true"]`
   - `#navigator-toolbox`
   - `#sidebar-box`
   - `menupopup`
   Run `python3 scripts/validate-minafox-ui.py` and confirm it fails before CSS changes.
2. Implement the chrome polish in `profile/userChrome.css`:
   - add named design tokens for command glow, rail background, active tab pill, button hover, and panel glass;
   - make the URL bar container behave more like a centered command bar using max-width/flex behavior where Firefox permits;
   - strengthen rounded command capsule focus glow;
   - make active tab pills use the named pink/violet pill token;
   - keep toolbar/sidebar/panel glass styling readable and scoped to known Firefox selectors.
3. Update README’s Hybrid MinaFox UI section to mention the Phase 2 chrome polish and profile-CSS limitations.
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
5. Independent review the resulting diff for spec compliance, maintainability, security, and Firefox selector risk.
6. Fix reviewer issues if any, re-run gates, then commit locally.

## Acceptance criteria
- RED failure observed after validator change and before CSS implementation.
- Final UI validator passes with the new required chrome tokens/selectors.
- SearXNG start-page search invariants remain unchanged.
- Existing standalone/package/telemetry/host-path validators still pass.
- Commit locally with a concise sprint commit message.

## Manual Firefox notes
A full graphical Firefox/DevTools visual check may be blocked in this headless environment. If so, report that honestly and rely on deterministic validators plus shell checks for this sprint.
