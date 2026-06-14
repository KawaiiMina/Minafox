# MinaFox packaged local SearXNG user-service sprint

## Goal

Make the optional local MinaFox SearXNG service practical from the Arch package, not only from a repo checkout:

- Package a systemd user unit for `minafox-searxng.service`.
- Let the packaged helper prepare a writable per-user SearXNG runtime directory under `~/.local/share/minafox/searxng`.
- Keep the service localhost-only at `127.0.0.1:8888`.
- Keep secrets out of git and out of `/usr/share` by generating `~/.local/share/minafox/searxng/.env` and `settings.yml.local`.
- Document simple start/status/logs commands.

## Current context / assumptions

- Existing overlay lives in `searxng/` and is already packaged under `/usr/share/minafox/searxng`.
- Existing helper is repo-root oriented and starts Compose detached.
- Existing package validates staged files via `scripts/validate-minafox-arch-package.py`.
- This sprint should not require real Docker daemon startup in this environment; config/shell/package simulation can be verified here. If Docker daemon access is unavailable, report that honestly.

## TDD approach

1. Extend validators first:
   - `scripts/validate-minafox-searxng.py` should require a systemd user unit, packaged/user-data runtime support, foreground service action, `systemctl --user` docs, and localhost-only binding.
   - `scripts/validate-minafox-arch-package.py` should require packaging/staging the user unit and the SearXNG helper executable.
2. Run the narrow validators and observe failure for missing new service requirements.
3. Implement the minimal files/script changes to satisfy the new tests.
4. Re-run narrow validators and then the full validation gate.

## Files likely to change

- `scripts/validate-minafox-searxng.py`
- `scripts/validate-minafox-arch-package.py`
- `scripts/install-minafox-searxng-arch.sh`
- `systemd/user/minafox-searxng.service` (new)
- `packaging/arch/minafox-profile-git/PKGBUILD`
- `packaging/arch/minafox-profile-git/.SRCINFO`
- `packaging/arch/minafox-profile-git/README.md`
- `searxng/README.md`
- `README.md`

## Implementation steps

1. Add failing validator requirements for:
   - `systemd/user/minafox-searxng.service` exists.
   - Unit uses `ExecStart=/usr/share/minafox/scripts/install-minafox-searxng-arch.sh service` and `ExecStop=... stop`.
   - Helper supports actions: `install-service`, `start`, `service`, `stop`, `status`, `logs`.
   - Helper copies packaged overlay from `/usr/share/minafox/searxng` into `$XDG_DATA_HOME/minafox/searxng` when running packaged.
   - Helper uses `systemctl --user` for the service path and parses `.env` as data.
   - Package stages `usr/lib/systemd/user/minafox-searxng.service` and `usr/share/minafox/scripts/install-minafox-searxng-arch.sh` executable.
2. Implement helper action model:
   - Default `start` -> prepare runtime dir, generate secret/local settings, run Compose detached.
   - `service` -> same prep but run `compose up --build` in foreground for systemd.
   - `stop` -> `compose down`.
   - `install-service` -> `systemctl --user daemon-reload && systemctl --user enable --now minafox-searxng.service`.
   - `status`/`logs` -> user-service inspection commands.
3. Add systemd user unit with safe restart behavior.
4. Update package staging and docs.
5. Verify.

## Validation / acceptance criteria

Automated:

```bash
python3 scripts/validate-minafox-searxng.py
python3 scripts/validate-minafox-arch-package.py
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-minafox-standalone.py
python3 scripts/validate-no-host-paths.py
python3 scripts/validate-no-firefox-telemetry.py
bash -n scripts/install-minafox-arch.sh scripts/install-minafox-searxng-arch.sh scripts/minafox-launcher.sh
python3 -m py_compile scripts/validate-minafox-searxng.py scripts/validate-minafox-arch-package.py
```

Compose/config:

```bash
docker compose -f searxng/docker-compose.yml config
```

If Docker/Compose is unavailable, record the blocker and use static/package validation instead.

Manual Arch handoff after package install:

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
```

Firefox/browser acceptance:

- MinaFox start page still posts searches to `http://127.0.0.1:8888/search`.
- Local service remains bound to localhost only.
- No committed secrets.

## Risks / rollback

- Different Compose implementations vary (`docker compose` vs `podman compose` vs `podman-compose`). Keep detection conservative and existing Docker/Podman paths.
- Rootless Podman service behavior may differ from Docker daemon behavior; document both and avoid claiming runtime start without actually starting it.
- `systemctl --user` requires a user session; if unavailable, helper should explain how to run `start` directly.
