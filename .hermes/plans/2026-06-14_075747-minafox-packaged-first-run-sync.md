# MinaFox sprint: packaged first-run profile sync

## Goal

Make the packaged `/usr/bin/minafox` usable on first launch by automatically syncing packaged assets from `/usr/share/minafox` into the dedicated user profile/local share paths when the user has installed the Arch package but has not manually run `/usr/share/minafox/scripts/install-minafox-arch.sh` yet.

## Context

- Previous sprint added `packaging/arch/minafox-profile-git` and validation.
- Current gap from README next steps: package installs `/usr/bin/minafox` and `/usr/share/minafox`, but profile/start-page assets still require a separate manual setup command.
- This is still a wrapper distribution using system Firefox, not a Firefox source fork.

## Approach

Use strict TDD via validators/smoke tests:

1. Extend `scripts/validate-minafox-standalone.py` to require launcher first-run sync behavior.
2. Run it first and verify RED.
3. Update `scripts/minafox-launcher.sh` to detect packaged assets and sync them idempotently before launching Firefox.
4. Keep `scripts/install-minafox-arch.sh` as the full installer for explicit updates, policy install, and source-tree installs.
5. Update package docs and top-level README to say package install now auto-syncs user assets on first launch, while the manual setup helper remains available for explicit refresh/policy install.

## Acceptance criteria

- Launcher supports configurable shared asset root via `MINAFOX_SHARE_DIR`, defaulting to `/usr/share/minafox`.
- On launch, if shared assets exist, launcher creates/syncs:
  - `$PROFILE_DIR/user.js` rendered from shared `profile/user.js` with real `file://` start URL.
  - `$PROFILE_DIR/chrome/userChrome.css`.
  - `$PROFILE_DIR/chrome/userContent.css` rendered with real start URL.
  - `$HOME/.local/share/minafox/start.html`.
  - `$HOME/.local/share/applications/minafox.desktop` when available.
  - hicolor icons into `$HOME/.local/share/icons/hicolor` when available.
- Existing `MINAFOX_PROFILE_DIR` and `MINAFOX_FIREFOX_BIN` overrides continue to work.
- Launcher still uses `MOZ_ENABLE_WAYLAND=1`, `--name minafox`, `--class MinaFox`, and passes args safely.
- No hardcoded author-machine paths are introduced.
- Package validator continues to pass.

## Files likely to change

- `scripts/minafox-launcher.sh`
- `scripts/validate-minafox-standalone.py`
- `README.md`
- `packaging/arch/minafox-profile-git/README.md`

## Verification

Run real gates:

```bash
python3 scripts/validate-minafox-standalone.py  # RED before implementation, GREEN after
bash -n scripts/install-minafox-arch.sh scripts/minafox-launcher.sh packaging/arch/minafox-profile-git/PKGBUILD packaging/arch/minafox-profile-git/minafox-profile-git.install
python3 -m py_compile scripts/validate-minafox-standalone.py scripts/validate-minafox-arch-package.py
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-minafox-standalone.py
python3 scripts/validate-minafox-arch-package.py
python3 scripts/validate-no-host-paths.py
python3 scripts/validate-no-firefox-telemetry.py
python3 scripts/validate-minafox-searxng.py
```

Add a non-mutating smoke test with temporary HOME, fake Firefox, and temporary `MINAFOX_SHARE_DIR` to prove first-run sync creates rendered files without touching the real profile.

## Risks

- Launcher side effects become heavier; keep it idempotent and limited to user-local files only.
- Avoid sudo/policy writes from the launcher. Enterprise policy install remains an explicit installer step.
- Use Python `Path.as_uri()` for start URL rendering so paths with spaces/special chars are safe.
