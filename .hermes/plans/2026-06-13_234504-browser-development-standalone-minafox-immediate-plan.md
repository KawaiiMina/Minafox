# MinaFox Standalone Browser — Better Immediate Plan

## Goal
Move MinaFox from “Firefox profile/theme scaffold” toward a **real standalone Firefox-derived browser**, without blocking the project on a full Firefox source fork immediately.

The immediate plan is two-track:

- **Track A: Design/UX prototype** — make MinaFox visually match the cosmic Arc/Zen-style mockup using maintainable profile CSS, a local start page, and optional Sidebery theming.
- **Track B: Standalone browser foundation** — turn the current repo into an installable standalone Arch app/distribution with its own launcher, package layout, profile namespace, branding, policies, and eventually a source-fork path.

This keeps momentum: MinaFox starts feeling like a real app soon, while preparing for the later source fork/native UI work.

## Current context

- Repo: `/home/hermes/Minafox`
- GitHub: `KawaiiMina/Minafox`
- Current repo already contains:
  - `profile/userChrome.css`
  - `profile/userContent.css`
  - `profile/user.js`
  - `desktop/start.html`
  - `desktop/minafox.desktop`
  - `distribution/policies.json`
  - `assets/` icon set
  - `searxng/` local private search overlay
  - `scripts/install-minafox-arch.sh`
  - validation scripts
- Current limitation: it is still conceptually a Firefox profile/distribution layer, not a fully separate browser binary.
- New product direction: Mina wants MinaFox to become a **real standalone browser**.

## Strategy

Do not jump straight into native Firefox UI work. Instead:

1. Build the desired look as a high-quality prototype on the current layer.
2. Package that layer as a standalone Arch app so Mina runs `minafox`, not a long Firefox command.
3. Create a source-fork research/build track once the standalone distribution works.
4. Port proven design/policy/start-page pieces into the fork.
5. Only then start native browser UI changes.

## Definition of “standalone” by milestone

## Milestone 1 — Standalone app wrapper/distribution
MinaFox is installed and launched as its own app, but still uses system Firefox underneath.

Expected user command:

```bash
minafox
```

Expected install/package-owned files:

```text
/usr/bin/minafox
/usr/share/applications/minafox.desktop
/usr/share/icons/hicolor/.../apps/minafox.png
/usr/share/minafox/start.html
/usr/share/minafox/profile/user.js.template
/usr/share/minafox/profile/userChrome.css
/usr/share/minafox/profile/userContent.css.template
/usr/share/minafox/distribution/policies.json.template
/usr/share/minafox/searxng/...
```

Expected runtime/user files:

```text
~/.mozilla/firefox/minafox/
~/.local/share/minafox/
```

This milestone is “standalone enough” for daily use while remaining easy to maintain.

## Milestone 2 — Arch package
MinaFox can be installed through a package-like workflow.

Possible package names:

- `minafox-profile-git` — current wrapper/profile distribution.
- `minafox-git` — later source-build package.
- `minafox-bin` — later prebuilt binary package.

Deliverable:

```text
packaging/arch/PKGBUILD
packaging/arch/minafox.install
packaging/arch/minafox.sh
```

Acceptance command:

```bash
makepkg -si
minafox
```

## Milestone 3 — Source fork foundation
Create and document the Firefox source fork path, but do not start deep UI surgery yet.

Deliverables:

```text
docs/forking/firefox-source-build.md
docs/forking/branding-patches.md
docs/forking/upstream-update-policy.md
patches/firefox-branding/README.md
```

Goals:

- Identify base: Firefox stable vs ESR.
- Document Arch build requirements.
- Document disk/time expectations.
- Build upstream Firefox once without custom patches.
- Add minimal branding patch only after clean upstream build succeeds.

## Milestone 4 — Branded source fork
MinaFox becomes a separate Firefox-derived binary.

Target outcomes:

- App name is MinaFox in the binary/build metadata where feasible.
- Own icons and desktop class.
- Own default profile/app data paths where feasible.
- MinaFox policies/prefs/start page are bundled.
- Current profile-layer UX is ported forward.

## Milestone 5 — Native UI fork
Only after the source fork builds and updates cleanly.

Target native UI features:

- built-in workspace rail
- native vertical tabs/workspaces
- native command palette behavior
- integrated dashboard/new-tab panels
- possible bottom floating toolbar

## Track A — Design/UX prototype tasks

These continue from the cosmic UI mockup plan.

### A1. Start page redesign

Files:

- `desktop/start.html`
- `scripts/validate-minafox-ui.py`
- `README.md`

Implement the screenshot-inspired start page first:

- cosmic purple/pink background
- floating workspace rail
- soft tab/workspace pills
- centered command/search bar
- “Good evening, Mina ✨” greeting
- quick app cards
- focus timer card
- notes/checklist card
- lofi/music card
- roadmap/Gantt card
- design-system card

Keep search behavior:

```html
<form role="search" method="post" action="http://127.0.0.1:8888/search">
  <input name="q" type="search">
</form>
```

Acceptance:

```bash
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-no-host-paths.py
```

Manual Firefox checks:

1. Install with `./scripts/install-minafox-arch.sh`.
2. Launch `minafox` once available, otherwise `firefox --profile ~/.mozilla/firefox/minafox`.
3. Check the start page visually matches the screenshot direction.
4. Tab through every interactive element.
5. Resize below 760px.
6. Open DevTools and verify no uncaught console errors.
7. Submit a harmless search and verify local SearXNG receives it.

### A2. Chrome polish

Files:

- `profile/userChrome.css`
- `profile/userContent.css`
- `scripts/validate-minafox-ui.py`

Tasks:

- Make Firefox URL bar look like a centered command bar.
- Strengthen glass toolbar styling.
- Improve soft tab pills.
- Improve sidebar styling for Firefox sidebar and future Sidebery.
- Keep selectors conservative and documented because Firefox chrome CSS is fragile.

Acceptance:

```bash
python3 scripts/validate-minafox-ui.py
bash -n scripts/install-minafox-arch.sh
```

Manual Firefox checks:

- active tab readable
- inactive tabs readable
- URL bar focus glow works
- menus/panels readable
- sidebar readable
- no unusable hidden browser controls

### A3. Real workspaces via Sidebery

Files likely:

- `distribution/policies.json`
- `profile/userChrome.css`
- `README.md`
- optional `profile/sidebery.css` or `extensions/sidebery-theme.css`

Tasks:

1. Choose Sidebery as the first real workspace/vertical tab layer.
2. Decide install method:
   - enterprise policy force-install if stable
   - documented manual install if policy is brittle
3. Add MinaFox Sidebery theme:
   - workspace colors: Personal, Work, Dev, Research
   - rounded active tab pill
   - pink/violet hover and active glow
4. Document manual import if needed.

Acceptance:

- MinaFox is usable without Sidebery.
- With Sidebery installed, it moves closer to the screenshot.
- No policy JSON errors.

## Track B — Standalone browser foundation tasks

## B1. Create `/usr/bin/minafox` launcher script

Files likely:

- `scripts/minafox-launcher.sh`
- `desktop/minafox.desktop`
- `scripts/install-minafox-arch.sh`
- `scripts/validate-minafox-install.py` or extension of existing validators

Launcher responsibilities:

- ensure dedicated MinaFox profile exists
- set Wayland-friendly env vars
- launch Firefox with MinaFox identity/class/profile
- prefer system Firefox for Milestone 1

Sketch:

```bash
#!/usr/bin/env bash
set -euo pipefail
export MOZ_ENABLE_WAYLAND=1
exec firefox --name minafox --class MinaFox --profile "$HOME/.mozilla/firefox/minafox" "$@"
```

Acceptance:

```bash
bash -n scripts/minafox-launcher.sh
./scripts/install-minafox-arch.sh
minafox --version || true
```

Manual:

- Desktop launcher starts MinaFox.
- Window class appears as MinaFox in Hyprland tools.
- It does not open the default Firefox profile.

## B2. Rework installer for package-like layout

Files likely:

- `scripts/install-minafox-arch.sh`
- `scripts/install-minafox-searxng-arch.sh`
- `scripts/validate-no-host-paths.py`

Add support for two modes:

1. **Developer mode** from repo:
   - current behavior
   - uses repo files directly
2. **Installed mode** from `/usr/share/minafox`:
   - copies templates/assets from system location
   - installs launcher to `/usr/bin/minafox` via package, not by ad-hoc sudo copying when possible

Acceptance:

- Running from repo still works.
- Running from installed layout works in a fake DESTDIR test.
- No hardcoded `/home/<user>` paths.

## B3. Add Arch packaging skeleton

Files to add:

```text
packaging/arch/PKGBUILD
packaging/arch/minafox.install
packaging/arch/minafox.sh
packaging/arch/README.md
```

Initial package type:

```text
minafox-profile-git
```

Dependencies:

- `firefox`
- `gtk-update-icon-cache` provider if needed
- optional `docker`/`podman` for SearXNG documented separately, not hard dependency unless we choose so

Package should install:

- launcher
- desktop file
- icons
- profile templates
- start page
- policy template
- docs

Acceptance:

```bash
cd packaging/arch
makepkg --printsrcinfo
makepkg -f
```

If package building cannot run in this environment, document blocker and validate file syntax as far as possible.

## B4. Add standalone validation gates

Files likely:

```text
scripts/validate-minafox-standalone.py
scripts/validate-no-host-paths.py
scripts/validate-minafox-ui.py
```

Validator should check:

- launcher exists and is executable
- desktop file uses `Exec=minafox` or the packaged launcher path
- icon is `minafox`, not Firefox
- package paths do not contain `/home/<user>`
- templates still contain placeholders where expected
- rendered files do not contain placeholders
- policy JSON is valid after rendering

Acceptance:

```bash
python3 scripts/validate-minafox-standalone.py
python3 scripts/validate-no-host-paths.py
```

## B5. Documentation update

Files:

- `README.md`
- `docs/standalone-roadmap.md`
- `docs/packaging-arch.md`

README should clearly say:

- Current phase: standalone wrapper/distribution.
- Future phase: Firefox source fork.
- Install commands.
- Launch command: `minafox`.
- How this differs from a full source fork.
- Known limitations.

## Track C — Source fork research and proof-of-build

This track should be documented before implemented.

## C1. Choose source base

Options:

- Firefox stable
  - Pros: latest features/security.
  - Cons: faster moving target.
- Firefox ESR
  - Pros: calmer, better for maintaining a fork.
  - Cons: older features.
- LibreWolf base
  - Pros: privacy patches already exist.
  - Cons: another downstream layer to understand.

Recommendation for MinaFox:

- Use **Firefox ESR** for the first source-fork proof unless Mina strongly wants latest Firefox UI/features.
- Keep the profile/package version independent so daily MinaFox remains usable while source work happens.

## C2. Document build requirements

File:

```text
docs/forking/firefox-source-build.md
```

Include:

- Arch packages required
- disk space estimate
- build time expectations
- `mach bootstrap`
- `mach build`
- `mach run`
- clean build vs incremental build
- expected failure modes

## C3. Clean upstream build

Do this before patches.

Acceptance:

```bash
./mach build
./mach run
```

No MinaFox changes until upstream builds successfully.

## C4. Minimal branding patch

Only after C3 succeeds.

Patch order:

1. app name strings
2. icons
3. desktop class/app ID where feasible
4. default prefs/policies/start page
5. package naming

No native UI changes in the first source-fork commit.

## Tests and validation summary

Current-layer validators:

```bash
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-no-host-paths.py
python3 scripts/validate-no-firefox-telemetry.py
python3 scripts/validate-minafox-searxng.py
bash -n scripts/install-minafox-arch.sh scripts/install-minafox-searxng-arch.sh
python3 -m json.tool distribution/policies.json >/dev/null
```

Future standalone validators:

```bash
python3 scripts/validate-minafox-standalone.py
cd packaging/arch && makepkg --printsrcinfo
```

Firefox manual verification:

1. Launch `minafox`.
2. Confirm it uses MinaFox profile, not default Firefox profile.
3. Confirm window class/name is MinaFox under Hyprland.
4. Confirm start page opens.
5. Confirm search submits to local SearXNG.
6. Confirm browser chrome theme applies.
7. Confirm no console errors on the start page.
8. Confirm keyboard navigation and focus rings.
9. Confirm responsive start page layout.

## Risks and mitigations

### Risk: Full Firefox fork slows everything down
Mitigation: keep Track A and B useful independently. Daily MinaFox should not depend on source fork success.

### Risk: Firefox chrome CSS breaks after updates
Mitigation: keep selectors conservative, validators explicit, README notes clear, and prefer Sidebery for vertical tabs.

### Risk: Standalone wrapper is confused with true source fork
Mitigation: documentation must label phases clearly:

- standalone wrapper/distribution now
- source-derived binary later

### Risk: Arch packaging requires root/system changes
Mitigation: support `DESTDIR` package tests and keep developer-mode installer working.

### Risk: Telemetry/privacy behavior differs in a fork
Mitigation: keep profile/policy validator and later add source-fork-specific privacy validation.

## Recommended first implementation sprint

Sprint 1 should produce a visible and useful standalone milestone:

1. Add `scripts/minafox-launcher.sh`.
2. Update `desktop/minafox.desktop` to launch `minafox`.
3. Update installer to install/link a local user launcher if no package exists yet.
4. Add `scripts/validate-minafox-standalone.py`.
5. Update README with “Standalone wrapper now, source fork later”.
6. Run validators.
7. Commit and push.

Then Sprint 2 can implement the cosmic mockup start page.

## Open decisions

1. Package name: `minafox-profile-git`, `minafox-git`, or both eventually?
2. Should SearXNG be optional or bundled as a package service?
3. Should launcher use system Firefox first, or should we also support LibreWolf as a backend?
4. Should source-fork base be Firefox ESR or stable?
5. Should Sidebery be forced-installed by policy or documented as a recommended setup step?

## Final recommendation

Proceed with the better immediate plan:

```text
1. Make MinaFox launch as `minafox`.
2. Package the current distribution cleanly for Arch.
3. Continue building the screenshot-inspired UI on the current layer.
4. Start source-fork research in docs/proof-build only after the standalone wrapper works.
5. Move native UI changes into the source fork only after a clean fork build exists.
```
