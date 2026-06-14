# Troubleshooting

## `minafox` command not found

For user-local installs, ensure `~/.local/bin` is on `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

For package installs, verify package files:

```bash
pacman -Ql minafox-profile-git | grep /usr/bin/minafox
```

## Browser opens but theme is missing

Run the installer/sync again:

```bash
cd ~/Minafox
./scripts/install-minafox-arch.sh
```

Check that `toolkit.legacyUserProfileCustomizations.stylesheets` is enabled in `profile/user.js`.

## Search is offline

```bash
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
cd ~/Minafox
./scripts/install-minafox-searxng-arch.sh start
```

Open `http://127.0.0.1:8888/`.

## AI Den says broker is offline

```bash
systemctl --user status minafox-ai-broker.service
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/providers
```

Start manually:

```bash
cd ~/Minafox
./scripts/minafox-ai-broker.sh
```

## Ollama chat does not enable

Make sure Ollama is running and the broker is explicitly allowed to chat:

```bash
curl http://127.0.0.1:11434/api/tags
MINAFOX_AI_ENABLE_OLLAMA_CHAT=1 ./scripts/minafox-ai-broker.sh
```

## Android page loads but search/AI points to the phone

On Android, `127.0.0.1` means the phone. Use the mobile harness and configure desktop/LAN URLs:

```bash
python3 scripts/serve-minafox-mobile.py \
  --host 0.0.0.0 \
  --mode lan-test \
  --harness-url http://<desktop-lan-ip>:8766 \
  --search-base-url http://<desktop-lan-ip>:8888 \
  --search-action-url http://<desktop-lan-ip>:8888/search \
  --ai-broker-url http://<desktop-lan-ip>:8765
```

Open `http://<desktop-lan-ip>:8766/`. If the page loads but the companion card shows a bad harness URL, set `MINAFOX_MOBILE_HARNESS_URL=http://<desktop-lan-ip>:8766` in the user-service override or pass `--harness-url` manually.

Diagnostics:

```bash
curl http://<desktop-lan-ip>:8766/health
curl http://<desktop-lan-ip>:8766/config
curl http://<desktop-lan-ip>:8766/android-checklist
```

## LAN broker refuses to start

For trusted LAN testing you need both the LAN flag and explicit origins:

```bash
MINAFOX_AI_BROKER_ALLOW_LAN=1 \
MINAFOX_AI_BROKER_ALLOWED_ORIGINS=http://<desktop-lan-ip>:8766 \
MINAFOX_AI_BROKER_HOST=0.0.0.0 \
./scripts/minafox-ai-broker.sh
```

Do not use wildcard CORS.

## `minafox-update` did not restart a service

`minafox-update` restarts services only when they are already active or enabled. Enable the service first:

```bash
systemctl --user enable --now minafox-ai-broker.service
systemctl --user enable --now minafox-searxng.service
systemctl --user enable --now minafox-mobile-harness.service
```

Then run `minafox-update`.

## Package validation fails

```bash
python3 scripts/validate-minafox-arch-package.py
git diff --check
bash -n scripts/*.sh
```
