# Mina AI Den

Mina AI Den is an optional start-page surface for local AI provider status and future chat. It is privacy-first and intentionally conservative.

## Current status

- Browser JavaScript calls only the MinaFox broker.
- The broker binds to `127.0.0.1:8765` by default.
- Local Ollama chat can be enabled explicitly.
- Cloud providers are metadata-only.
- Hermes Gateway is detection-only until pairing/auth and tool-safety UX exist.

## Broker endpoints

- `GET /health`
- `GET /providers`
- `GET /hermes/health`
- `POST /test-provider`
- `POST /chat` — local Ollama only, disabled unless `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1` is set.

## Run broker from checkout

```bash
cd ~/Minafox
./scripts/minafox-ai-broker.sh
```

Enable local Ollama chat:

```bash
MINAFOX_AI_ENABLE_OLLAMA_CHAT=1 ./scripts/minafox-ai-broker.sh
```

## Run broker as installed service

```bash
systemctl --user enable --now minafox-ai-broker.service
systemctl --user status minafox-ai-broker.service
```

## Provider modes

- **Local** — Ollama, local-first.
- **Cloud** — OpenAI / ChatGPT-compatible APIs, Gemini, Claude, OpenRouter. Metadata only for now.
- **LAN / advanced** — Hermes Gateway detection. Chat is blocked until explicit safety UX exists.

## Secrets policy

Never store provider keys in `desktop/start.html`, `profile/user.js`, localStorage, committed config, or static assets. Future secrets should come from environment variables, a local config file, or an OS keyring.

## Hermes Gateway boundary

Hermes Gateway can reach tool-capable agents, so it is treated as more powerful than a normal chat provider. It needs localhost-first operation, explicit pairing/auth, clear warnings, and no arbitrary tool toggles from browser UI before chat can be enabled.

## Validation

```bash
python3 scripts/test-minafox-ai-broker.py
python3 scripts/validate-minafox-ai.py
```
