# Services

MinaFox ships optional systemd user units for local search, the Mina AI Den broker, and the Android/LAN UX harness. The Arch package installs the units, scripts, and supporting assets, but it does not auto-enable these services for you.

All services are part of the standalone wrapper/profile release. They do not turn MinaFox into a compiled Firefox fork, do not bundle a Firefox binary, and do not add cloud/Hermes chat behavior.

## Overview

| Service | Purpose | Default bind | Auto-enabled |
|---|---|---|---|
| `minafox-searxng.service` | local private search through SearXNG | `127.0.0.1:8888` via Compose | No |
| `minafox-ai-broker.service` | Mina AI Den provider status broker | `127.0.0.1:8765` | No |
| `minafox-mobile-harness.service` | Android/LAN UX test harness | `0.0.0.0:8766` | No |

## Local search service

MinaFox's start page uses SearXNG as the local search layer at `http://127.0.0.1:8888/search`. Upstream engines are managed in SearXNG settings; MinaFox does not add direct browser-side Google, DuckDuckGo, Brave, Startpage, or other upstream engine integrations.

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh status
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
```

The helper copies the packaged overlay to `~/.local/share/minafox/searxng`, generates local runtime config/secrets there, and starts Docker/Podman Compose.

Stop it with:

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh stop
systemctl --user disable minafox-searxng.service
```

## AI broker service

The broker defaults to `127.0.0.1:8765` and supports provider metadata/status checks. Local Ollama chat remains disabled unless you explicitly opt in with `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1`. Cloud providers are metadata-only, and Hermes Gateway is detection-only until secrets/auth storage and tool-safety UX exist.

```bash
systemctl --user enable --now minafox-ai-broker.service
systemctl --user status minafox-ai-broker.service
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/providers
```

The service defaults to `MINAFOX_AI_BROKER_HOST=127.0.0.1` and `MINAFOX_AI_BROKER_PORT=8765`.

Stop it with:

```bash
systemctl --user disable --now minafox-ai-broker.service
```

## Mobile harness service

Enable only on a trusted LAN/Tailscale network:

```bash
systemctl --user enable --now minafox-mobile-harness.service
systemctl --user status minafox-mobile-harness.service
curl http://127.0.0.1:8766/health
curl http://127.0.0.1:8766/config
curl http://127.0.0.1:8766/android-checklist
```

The packaged service defaults to `0.0.0.0:8766` for explicit phone testing. This is not a default public service. Keep your firewall/router from exposing it to untrusted networks.

For a stable phone-visible URL, override `MINAFOX_MOBILE_HARNESS_URL=http://<desktop-lan-ip>:8766` or use a Tailscale hostname. If it is not set, the harness uses the incoming `Host` header for generated `/health`, `/config`, and `/android-checklist` links.

Stop it with:

```bash
systemctl --user disable --now minafox-mobile-harness.service
```

## Updating services

`minafox-update` refreshes the installed profile/start-page assets after package installation, then runs `systemctl --user daemon-reload` and restarts MinaFox services that are already active or enabled:

```bash
minafox-update
minafox-update --no-restart-services
```

## Logs

```bash
journalctl --user -u minafox-searxng.service -f
journalctl --user -u minafox-ai-broker.service -f
journalctl --user -u minafox-mobile-harness.service -f
```

For service failure triage, see [Troubleshooting](Troubleshooting). For release limits around optional services and LAN exposure, see [Known Limitations](Known-Limitations).
