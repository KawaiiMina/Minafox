# MinaFox Cosmic Arc UI Implementation Plan

## Goal
Make MinaFox look like the provided mockup: a cozy purple/pink glass browser with a floating left workspace rail, soft tab pills, a centered command/search bar, a cosmic start page, card-based widgets, and a subtle bottom mini-toolbar feel — while keeping the first version maintainable on top of Firefox profile CSS and a local `desktop/start.html`.

## Visual target from the mockup

Key components to reproduce:

1. **Overall shell**
   - Dark cosmic purple background with galaxy/nebula lighting.
   - Rounded browser window feel with translucent glass surfaces.
   - Pink/violet glow accents and thin lavender borders.

2. **Floating workspace rail**
   - Left vertical rail with MinaFox logo/title.
   - Circular workspace buttons: Personal, Work, Dev, Research.
   - Soft floating effect, separated from main content by a faint vertical line.

3. **Soft tab pills**
   - Vertical tab list with rounded pill tabs.
   - Active tab is pink gradient/glow.
   - Each tab has a small icon/paw and close button.
   - “New Tab” pill at the bottom.

4. **Centered command/search bar**
   - Command/search bar floating near the top center.
   - Rounded capsule with glass blur, pink focus glow, left sparkle icon, shortcut hint, right paw/action button.

5. **Cozy start page**
   - Greeting: “Good evening, Mina ✨”.
   - Subtitle line.
   - Large centered search input.
   - Quick app cards: Notes, Calendar, Mail, Drive, Figma, GitLab, YouTube, Add.
   - Widget cards: focus timer, notes checklist, music/lofi list.
   - Right-side dashboard cards: roadmap/Gantt, design-system palette/typography.

6. **Subtle mini-toolbar**
   - Bottom floating toolbar-like strip with small icons.
   - In Firefox profile CSS this can only be approximated by styling the real nav/personal toolbar; a true in-content bottom browser toolbar requires deeper customization or an extension.

## Feasibility split

### Feasible in the current profile/start-page layer
Use these first:

- `profile/userChrome.css`
  - Dark glass browser chrome.
  - Rounded URL/search bar.
  - More centered/narrow URL bar styling.
  - Soft tab pills for existing Firefox tabs.
  - Sidebar glass styling for Firefox sidebar / Sidebery container.
  - Toolbar button hover/focus glow.
  - Window-control area harmonized with the theme.

- `desktop/start.html`
  - Full mockup-like cosmic start page.
  - Greeting, search, quick cards, focus timer, notes checklist, lofi card, roadmap card, design-system card.
  - Responsive fallback for smaller windows.
  - Accessible keyboard navigation and visible focus rings.

- `profile/userContent.css`
  - Scoped support styling for the local start page and Firefox start surfaces only.

- `scripts/validate-minafox-ui.py`
  - Deterministic checks that the new UI structure/classes exist.

### Feasible but needs a curated extension/later step

- Real Arc-like vertical tab/workspace behavior:
  - Use Sidebery or Tree Style Tab.
  - Theme its sidebar with `userChrome.css` where possible.
  - Use containers/workspaces to approximate Personal/Work/Dev/Research.

- Command palette behavior beyond normal URL bar:
  - Firefox URL bar can look like a command bar.
  - A real custom command launcher requires a WebExtension or deeper browser work.

### Requires deeper Firefox source/custom browser work

- True browser-owned floating workspace rail independent of sidebar.
- True bottom mini-toolbar that controls browser UI outside web content.
- Native browser dashboard panels on the right that persist across pages.
- Replacing Firefox tab model/window layout at the engine/UI source level.

For this project, build **Phase 1 and Phase 2** first at profile/start-page level. Treat deeper source work as a separate future project after the visual direction is proven.

## Proposed implementation phases

## Phase 0 — Baseline and visual tokens

### Tasks
1. Confirm the repo is clean and current.
2. Create a shared MinaFox design token map used by both chrome CSS and start page:
   - Backgrounds: `#0f0b1e`, `#151126`, `#211936`.
   - Glass: `rgba(32, 24, 52, 0.62)`, `rgba(63, 48, 86, 0.78)`.
   - Borders: `rgba(245, 194, 231, 0.22)`.
   - Glow pink: `#ff79c6` / `rgba(255, 121, 198, 0.34)`.
   - Lavender: `#cba6f7`.
   - Violet: `#8b5cf6`.
   - Peach accent: `#ff9f8a`.
3. Decide whether to use pure CSS gradients for the galaxy background or add a local asset under `assets/`.

### Acceptance criteria
- Tokens are documented in comments.
- No hardcoded host paths.
- Theme still passes current validators.

## Phase 1 — Start page mockup MVP

### Files likely to change
- `desktop/start.html`
- `scripts/validate-minafox-ui.py`
- `README.md`

### Tasks
1. Add a mockup-inspired layout to `desktop/start.html`:
   - `main.minafox-desktop`
   - `aside.workspace-rail`
   - `section.soft-tabs`
   - `section.start-stage`
   - `section.dashboard-grid`
   - `nav.quick-apps`
   - `section.widget-grid`
2. Use static/dummy local widgets first:
   - Focus timer card: `45:00`, “Deep Work”, Start button.
   - Notes card: checklist of 3–4 items.
   - Lofi card: album tile, play button, list of tracks.
   - Roadmap card: CSS-only Gantt bars.
   - Design system card: palette swatches and typography sample.
3. Keep the existing SearXNG search form:
   - `method="post"`
   - `action="http://127.0.0.1:8888/search"`
   - `input name="q"`
   - accessible label.
4. Add responsive behavior:
   - Desktop: left rail + main dashboard grid.
   - Medium width: dashboard stacks below hero.
   - Narrow/mobile: rail becomes horizontal or hidden, cards become one column.
5. Add `prefers-reduced-motion` support.
6. Preserve required quick links from existing validation:
   - ChatGPT
   - GitHub
   - YouTube
   - Settings
   - Profiles

### TDD / validation
Before implementation, update `scripts/validate-minafox-ui.py` to require new structural classes and run it to observe RED:

```bash
python3 scripts/validate-minafox-ui.py
```

Expected RED failures should mention missing new mockup classes, e.g.:

- `workspace-rail`
- `soft-tab-list`
- `command-bar`
- `dashboard-grid`
- `focus-timer-card`
- `roadmap-card`
- `design-system-card`

After implementation, run:

```bash
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-no-host-paths.py
```

Manual Firefox checks:

1. Run `./scripts/install-minafox-arch.sh`.
2. Launch `firefox --profile ~/.mozilla/firefox/minafox`.
3. Confirm the start page resembles the mockup at a normal desktop size.
4. Press `Tab` through all interactive items; focus rings must be visible.
5. Resize below 760px and confirm no cards overflow.
6. Open DevTools on the start page and confirm no uncaught console errors.
7. Submit a test search and confirm it POSTs to local SearXNG.

## Phase 2 — Browser chrome closer to the mockup

### Files likely to change
- `profile/userChrome.css`
- `profile/userContent.css`
- `scripts/validate-minafox-ui.py`
- `README.md`

### Tasks
1. Make the top URL bar feel like a centered command bar:
   - Limit/max-width the URL bar container where Firefox permits.
   - Increase capsule rounding.
   - Stronger pink glow on focus.
   - Add subtle command-palette visual language through icons/focus styling.
2. Strengthen glass styling for:
   - `#navigator-toolbox`
   - `#nav-bar`
   - `#urlbar-background`
   - toolbar buttons
   - panel popups
3. Refine tab pills:
   - More vertical padding and rounded active state.
   - Pink/violet active glow.
   - Softer hover state.
4. Refine sidebar styling for future Sidebery/Firefox sidebar:
   - Glass rail colors.
   - Rounded internal sidebar items where Firefox exposes selectors safely.
   - Do **not** rely on overly brittle deep selectors for the first pass.
5. Approximate bottom mini-toolbar only if feasible without breaking Firefox UI:
   - Style existing bottom/status-like available areas conservatively.
   - Otherwise leave as a start-page-only decorative element and document the limitation.

### TDD / validation
Update `scripts/validate-minafox-ui.py` to require chrome tokens/selectors for the new design:

- `--mf-command-glow`
- `--mf-rail-bg`
- `--mf-pill-active`
- `#urlbar-background`
- `.tabbrowser-tab[selected]`
- `#sidebar-box`

Run RED, implement, then GREEN:

```bash
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-no-host-paths.py
bash -n scripts/install-minafox-arch.sh
```

Manual Firefox checks:

1. Install profile.
2. Launch MinaFox.
3. Confirm URL bar focus glow and rounded command-bar styling.
4. Open multiple tabs and confirm active/inactive tab contrast.
5. Open Firefox sidebar/bookmarks/history and confirm it remains readable.
6. Open menus/panels and confirm text contrast is good.
7. Check Web Console for start page errors.

## Phase 3 — Real workspaces / vertical tabs via extension

### Recommended direction
Use Sidebery as the practical way to get Arc-like workspaces without forking Firefox.

### Files likely to change
- `distribution/policies.json`
- `profile/userChrome.css`
- `README.md`
- Possibly `profile/sidebery.css` or `extensions/sidebery/` if we store extension theme snippets.

### Tasks
1. Decide extension:
   - Sidebery recommended for panels/workspaces/containers.
   - Tree Style Tab if simpler vertical tabs are enough.
2. Add extension installation policy if the extension ID/download source is stable.
3. Add a MinaFox Sidebery theme snippet:
   - workspace icons/colors: Personal, Work, Dev, Research.
   - active tab pink pill.
   - rounded tab list.
4. Document manual Sidebery import steps if policy cannot configure everything.
5. Validate policy JSON.

### Acceptance criteria
- Extension installs or instructions are clear.
- Sidebar looks close to the mockup.
- Browser remains usable without the extension installed.

## Phase 4 — Optional WebExtension dashboard/command palette

### Purpose
Only do this if the static start page is not enough.

### Possible features
- Custom new-tab extension replacing `desktop/start.html`.
- Persistent notes/focus timer via browser storage.
- Command palette overlay with keyboard shortcut.
- Workspace shortcuts/actions.

### Files likely to add
- `extension/manifest.json`
- `extension/newtab.html`
- `extension/src/*`
- `extension/styles/*`
- `scripts/validate-minafox-extension.py`

### Validation
- `npx web-ext lint` if Node tooling is available.
- Temporary load through `about:debugging` → This Firefox → Load Temporary Add-on.
- Check extension console/background errors.

## Phase 5 — Documentation and packaging

### Files likely to change
- `README.md`
- `searxng/README.md` if search/start-page interaction changes
- Future: `PKGBUILD` / package docs

### Tasks
1. Update README with:
   - Screenshot/design target description.
   - Install command.
   - Validation commands.
   - Manual Firefox verification steps.
   - Known limitations: profile CSS vs true browser fork.
2. Add a small “Design limits” section:
   - Profile CSS can style Firefox chrome but not fully redesign browser architecture.
   - Real workspaces should use Sidebery first.
   - Bottom native toolbar requires deeper work.
3. Consider adding screenshot assets after implementation.

## Suggested implementation order

1. **Start page first** — biggest visual win, least brittle.
2. **Chrome polish second** — URL bar, tabs, sidebar glass.
3. **Sidebery/workspaces third** — real vertical tabs/workspaces.
4. **Extension/source work later** — only if profile layer cannot satisfy the UX.

## Rollback plan

- Start page changes can be reverted by restoring `desktop/start.html`.
- Chrome changes can be reverted by restoring `profile/userChrome.css` and reinstalling with `./scripts/install-minafox-arch.sh`.
- Sidebery/extension changes should be optional and not required for basic browsing.
- Keep validators updated so partial/broken visual changes fail before install.

## Open decisions for Mina

1. Do you want the start page widgets to be **static decorative cards first**, or should focus timer/notes/music be functional from the beginning?
2. Do you want real vertical tabs/workspaces through **Sidebery**, or only the visual style for now?
3. Should the galaxy background be **pure CSS** for no extra assets, or should we generate/use a local image asset for a closer look?
4. Should the right-side roadmap/design-system cards be MinaFox project-specific, or generic cozy dashboard content?

## Definition of done for the first implementation PR/commit

- `desktop/start.html` visually matches the mockup direction: cosmic glass, left rail, command/search, widget cards, dashboard cards.
- Firefox chrome has improved centered command-bar styling, soft tabs, lavender glass surfaces.
- Search still submits to local SearXNG via POST.
- Keyboard focus is visible and responsive layout works.
- Validators pass:

```bash
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-no-host-paths.py
python3 scripts/validate-no-firefox-telemetry.py
python3 scripts/validate-minafox-searxng.py
bash -n scripts/install-minafox-arch.sh scripts/install-minafox-searxng-arch.sh
python3 -m json.tool distribution/policies.json >/dev/null
```

- Manual Firefox verification is completed or blockers are documented.
