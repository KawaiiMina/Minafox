# Development Guide

## Local workflow

```bash
cd ~/Minafox
git status --short
```

Make changes, then run the validation gate before committing.

## Full validation gate

```bash
python3 scripts/test-serve-minafox-mobile.py
python3 scripts/test-minafox-ai-broker.py
python3 scripts/test-minafox-update.py
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-minafox-standalone.py
python3 scripts/validate-minafox-arch-package.py
python3 scripts/validate-no-host-paths.py
python3 scripts/validate-no-firefox-telemetry.py
python3 scripts/validate-minafox-searxng.py
python3 scripts/validate-minafox-ai.py
bash -n scripts/minafox-update.sh scripts/minafox-launcher.sh scripts/minafox-ai-broker.sh scripts/install-minafox-arch.sh scripts/install-minafox-searxng-arch.sh
python3 -m py_compile scripts/serve-minafox-mobile.py scripts/minafox-ai-broker.py scripts/test-minafox-update.py
git diff --check
```

## Manual browser checks

1. Run `./scripts/install-minafox-arch.sh` or `minafox-update`.
2. Launch `minafox`.
3. Verify browser chrome, start page, focus rings, quick links, Settings/Profile buttons, and narrow viewport behavior.
4. Open DevTools and confirm no console errors.

## Manual service checks

```bash
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8766/health
curl http://127.0.0.1:8888/
```

## UI development rules

- Keep the MinaFox style calm, dark, glassy, pink/purple, and readable.
- Prefer visible focus rings and reduced-motion support over flashy effects.
- Keep mobile touch targets comfortable.
- Do not force extensions by policy unless that decision is explicit.
- Keep Firefox internal selector changes conservative; `userChrome.css` can break across Firefox versions.

## AI/security development rules

- No secrets in static files.
- No wildcard CORS for LAN broker mode.
- No `null` or `file://` origins for non-loopback broker binds.
- Hermes Gateway must stay blocked until pairing/auth and tool-safety UX exist.

## Commit hygiene

```bash
git status --short --untracked-files=all
git diff --check
git add <intentional files>
git commit -m "type: short description"
```

Recommended commit types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
