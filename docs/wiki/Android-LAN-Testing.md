# Android/LAN Testing

Firefox for Android does not load the desktop `userChrome.css` wrapper, so MinaFox uses a lightweight web harness to test responsive UX and touch behavior before native Android/WebView/Fenix work.

## What the harness does

`serve-minafox-mobile.py` serves `desktop/start.html` and injects `window.MINAFOX_RUNTIME_CONFIG` before the start-page script runs. That lets Android call services on the desktop/LAN host instead of phone-local `127.0.0.1`.

## Run from a checkout

```bash
cd ~/Minafox
python3 scripts/serve-minafox-mobile.py \
  --host 0.0.0.0 \
  --mode lan-test \
  --search-base-url http://<desktop-lan-ip>:8888 \
  --search-action-url http://<desktop-lan-ip>:8888/search \
  --ai-broker-url http://<desktop-lan-ip>:8765
```

Open on Android:

```text
http://<desktop-lan-ip>:8766/
```

## Run from the packaged service

```bash
systemctl --user enable --now minafox-mobile-harness.service
systemctl --user status minafox-mobile-harness.service
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
```

Apply:

```bash
systemctl --user daemon-reload
systemctl --user restart minafox-mobile-harness.service
```

## Security rules

- Only bind to `0.0.0.0` on trusted LAN/Tailscale networks.
- Do not expose port `8766` to the public internet.
- Do not put provider keys in `desktop/start.html`, localStorage, or the harness.
- If exposing the AI broker to Android, use explicit CORS origins; never `*`, `null`, or `file://`.

## AI broker over LAN

```bash
MINAFOX_AI_BROKER_ALLOW_LAN=1 \
MINAFOX_AI_BROKER_ALLOWED_ORIGINS=http://<desktop-lan-ip>:8766 \
MINAFOX_AI_ENABLE_OLLAMA_CHAT=1 \
MINAFOX_AI_BROKER_HOST=0.0.0.0 \
./scripts/minafox-ai-broker.sh
```

## UX checklist

Check 360 px, 390 px, 430 px, and 768 px widths. Verify readable search, stacked AI Den cards, no ugly panning, calm offline copy, visible focus states, and no console errors.
