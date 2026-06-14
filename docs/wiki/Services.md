# Services

MinaFox ships optional systemd user units. They are installed by the Arch package but should be enabled deliberately.

## Overview

| Service | Purpose | Default bind |
|---|---|---|
| `minafox-searxng.service` | local private search | `127.0.0.1:8888` via Compose |
| `minafox-ai-broker.service` | Mina AI Den broker | `127.0.0.1:8765` |
| `minafox-mobile-harness.service` | Android/LAN UX test harness | `0.0.0.0:8766` |

## Local search service

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
```

The helper copies the packaged overlay to `~/.local/share/minafox/searxng`, generates local runtime config/secrets there, and starts Docker/Podman Compose.

## AI broker service

```bash
systemctl --user enable --now minafox-ai-broker.service
systemctl --user status minafox-ai-broker.service
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/providers
```

The service defaults to `MINAFOX_AI_BROKER_HOST=127.0.0.1` and `MINAFOX_AI_BROKER_PORT=8765`.

## Mobile harness service

Enable only on a trusted LAN/Tailscale network:

```bash
systemctl --user enable --now minafox-mobile-harness.service
systemctl --user status minafox-mobile-harness.service
curl http://127.0.0.1:8766/health
curl http://127.0.0.1:8766/config
curl http://127.0.0.1:8766/android-checklist
```

The packaged service defaults to `0.0.0.0:8766` for phone testing. Keep your firewall/router from exposing this to untrusted networks.

For a stable phone-visible URL, override `MINAFOX_MOBILE_HARNESS_URL=http://<desktop-lan-ip>:8766` or use a Tailscale hostname. If it is not set, the harness uses the incoming `Host` header for generated `/health`, `/config`, and `/android-checklist` links.

## Updating services

`minafox-update` runs `systemctl --user daemon-reload` after package installation, then restarts MinaFox services that are already active or enabled:

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
