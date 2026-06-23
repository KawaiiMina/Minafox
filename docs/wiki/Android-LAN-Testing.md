# Android/LAN Testing

Firefox for Android does not load the desktop `userChrome.css` wrapper, so MinaFox uses a lightweight web harness to test responsive UX and touch behavior before native Android/WebView/Fenix work.

The harness is an explicit trusted-network testing tool, not a default public service. The Arch package installs the user unit, but it does not auto-enable it.

## What the harness does

`serve-minafox-mobile.py` serves `desktop/start.html` and injects `window.MINAFOX_RUNTIME_CONFIG` before the start-page script runs. That lets Android call services on the desktop/LAN host instead of phone-local `127.0.0.1`.

## Run from a checkout

Use this only on a trusted LAN/Tailscale network:

```bash
cd ~/Minafox
python3 scripts/serve-minafox-mobile.py \
  --host 0.0.0.0 \
  --mode lan-test \
  --harness-url http://<desktop-lan-ip>:8766 \
  --search-base-url http://<desktop-lan-ip>:8888 \
  --search-action-url http://<desktop-lan-ip>:8888/search \
  --ai-broker-url http://<desktop-lan-ip>:8765
```

Open on Android:

```text
http://<desktop-lan-ip>:8766/
```

Useful diagnostics from the phone:

```text
http://<desktop-lan-ip>:8766/health
http://<desktop-lan-ip>:8766/config
http://<desktop-lan-ip>:8766/android-checklist
```

The start page also shows an **Android/LAN test companion** card with the active mode, search URL, AI broker URL, harness health URL, and a short touch checklist. The harness prefers the phone-visible `Host` header for these links unless you set `--harness-url` / `MINAFOX_MOBILE_HARNESS_URL` explicitly.

## Run from the packaged service

```bash
systemctl --user enable --now minafox-mobile-harness.service
systemctl --user status minafox-mobile-harness.service
curl http://127.0.0.1:8766/health
curl http://127.0.0.1:8766/config
curl http://127.0.0.1:8766/android-checklist
```

Override URLs with a user-service override if Android should use a specific LAN/Tailscale hostname:

```bash
systemctl --user edit minafox-mobile-harness.service
```

```ini
[Service]
Environment=MINAFOX_MOBILE_SEARCH_BASE_URL=http://<desktop-lan-ip>:8888
Environment=MINAFOX_MOBILE_SEARCH_ACTION_URL=http://<desktop-lan-ip>:8888/search
Environment=MINAFOX_MOBILE_AI_BROKER_URL=http://<desktop-lan-ip>:8765
Environment=MINAFOX_MOBILE_HARNESS_URL=http://<desktop-lan-ip>:8766
```

Apply:

```bash
systemctl --user daemon-reload
systemctl --user restart minafox-mobile-harness.service
```

Stop it when testing is done:

```bash
systemctl --user disable --now minafox-mobile-harness.service
```

## Security rules

- Only bind to `0.0.0.0` on trusted LAN/Tailscale networks.
- Do not expose port `8766` to the public internet.
- Do not put provider keys in `desktop/start.html`, localStorage, or the harness.
- If exposing the AI broker to Android, use explicit CORS origins; never `*`, `null`, or `file://`.
- Keep SearXNG on local/trusted network paths; do not publish `127.0.0.1:8888` through a router or public reverse proxy.

## AI broker over LAN

This is optional and only for trusted LAN/Tailscale testing. Ollama chat remains disabled unless `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1` is set explicitly, and cloud providers/Hermes Gateway remain metadata/detection-only in this release.

```bash
MINAFOX_AI_BROKER_ALLOW_LAN=1 \
MINAFOX_AI_BROKER_ALLOWED_ORIGINS=http://<desktop-lan-ip>:8766 \
MINAFOX_AI_ENABLE_OLLAMA_CHAT=1 \
MINAFOX_AI_BROKER_HOST=0.0.0.0 \
./scripts/minafox-ai-broker.sh
```

## UX checklist

Check 360 px, 390 px, 430 px, and 768 px widths. Verify readable search, stacked AI Den cards, no ugly panning, calm offline copy, visible focus states, and no console errors. Use `/android-checklist` for a phone-friendly checklist you can keep open while testing.

For unreachable phone, service, and CORS triage, see [Troubleshooting](Troubleshooting). For the trusted-network-only release boundary, see [Known Limitations](Known-Limitations).
