# MinaFox AI Provider Architecture

MinaFox AI is optional. The browser start page may show a calm **Mina AI Den**, but real provider calls should go through a future localhost-only broker instead of direct browser JavaScript.

## Design goals

- Keep browsing calm: the AI panel starts disabled and does not nag.
- Keep secrets out of static files: secrets must not be committed, stored in `desktop/start.html`, stored in `profile/user.js`, or placed in browser localStorage.
- Prefer local-first operation: Ollama is the first practical provider because it can run on `127.0.0.1`.
- Treat cloud providers clearly as Cloud mode.
- Treat Hermes Gateway clearly as LAN / advanced mode because Hermes Gateway can trigger tool-capable agents depending on the paired Hermes install.

## Provider modes

## Local broker and Hermes API Server

MinaFox uses a localhost-only broker boundary before it talks to Hermes or any
cloud provider:

```text
MinaFox start page
  -> http://127.0.0.1:8765
MinaFox AI broker
  -> http://127.0.0.1:8642
Hermes API Server gateway
  -> Hermes Agent
```

The first broker sprint exposes only safe discovery endpoints:

- `GET /health`
- `GET /providers`
- `GET /hermes/health`
- `POST /chat` accepts only local Ollama payloads in the current phase. It is
  disabled unless `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1` is set, and it never routes
  prompts to Hermes Gateway or cloud providers.
- `POST /test-provider` currently checks only local Ollama health.

Hermes itself is expected to run the API Server gateway on loopback with
`API_SERVER_ENABLED=true` and an `API_SERVER_KEY` stored in a user-local secret
file or environment, never in this repository and never in `desktop/start.html`.
The broker reads that key through `HERMES_API_SERVER_KEY` or `API_SERVER_KEY`
when it needs to call authenticated Hermes endpoints.

- **Local:** Ollama, local-only by default.
- Cloud: **OpenAI**, **ChatGPT-compatible** APIs, **Gemini**, **Claude**, and **OpenRouter**.
- LAN: **Hermes Gateway** after explicit host configuration, pairing, and warning copy.

The UI labels these as **Local / Cloud / LAN** so it is obvious where prompts may go.

## Future localhost-only broker

The future broker should bind to `127.0.0.1` only and expose a small API:

- `GET /health`
- `GET /providers`
- `POST /chat`
- `POST /test-provider`

The broker reads user-local configuration from:

```text
~/.config/minafox/ai.yaml
```

API keys should be resolved from environment variables or a future OS keyring integration. Example names may include `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, and `OPENROUTER_API_KEY`, but this repo must not contain actual values.

## Hermes Gateway safety rules

Hermes Gateway is more powerful than a normal chat provider. A prompt sent to a paired Hermes install may run an agent and use tools, depending on that Hermes configuration.

Rules before implementation:

1. Start with localhost Hermes only.
2. LAN Hermes must be explicitly configured by host/IP; no automatic trust or discovery.
3. Require pairing/auth before sending prompts.
4. Show warnings that Hermes Gateway can trigger tool-capable agents.
5. Do not pass MinaFox cloud provider keys to Hermes unless the user explicitly configures that.
6. Do not expose arbitrary tool toggles from browser UI.

## Current phase

The current broker sprint keeps cloud and Hermes chat disabled, but it can light
up **local Ollama** when the loopback Ollama API is reachable. Ollama chat can be
enabled with:

```bash
MINAFOX_AI_ENABLE_OLLAMA_CHAT=1 minafox-ai-broker
```

The start page then enables only the Ollama prompt controls through
`http://127.0.0.1:8765/chat`. Cloud providers remain metadata-only until secrets
storage is implemented, and Hermes Gateway remains detection-only until a
separate pairing/auth and tool-safety UX exists.

## Android/LAN UX harness

Firefox for Android does not load the desktop `userChrome.css` wrapper, so MinaFox
uses a browser-facing **Android/LAN UX harness** for responsive testing instead of
building a full Firefox/Fenix APK during early UI work.

The harness serves `desktop/start.html` and injects runtime service URLs before
the start-page script runs:

```text
Android browser
  -> http://<desktop-or-tailscale-host>:8766/
MinaFox mobile harness
  -> configured SearXNG base URL
  -> configured minafox-ai-broker URL
```

Desktop defaults stay loopback-first. Android test mode must be explicit because
`127.0.0.1` from a phone means the phone itself, not the desktop running SearXNG,
Ollama, or the broker.

Example trusted-LAN test commands:

```bash
python3 scripts/serve-minafox-mobile.py \
  --host 0.0.0.0 \
  --mode lan-test \
  --search-base-url http://<desktop-lan-ip>:8888 \
  --search-action-url http://<desktop-lan-ip>:8888/search \
  --ai-broker-url http://<desktop-lan-ip>:8765

MINAFOX_AI_BROKER_ALLOW_LAN=1 \
MINAFOX_AI_BROKER_ALLOWED_ORIGINS=http://<desktop-lan-ip>:8766 \
MINAFOX_AI_ENABLE_OLLAMA_CHAT=1 \
MINAFOX_AI_BROKER_HOST=0.0.0.0 \
./scripts/minafox-ai-broker.sh
```

LAN broker access is for trusted local/Tailscale testing only. The broker refuses
non-loopback binds unless `MINAFOX_AI_BROKER_ALLOW_LAN=1` is set, and CORS uses
`MINAFOX_AI_BROKER_ALLOWED_ORIGINS` rather than `*`. Do not put cloud provider
keys in the harness, start page, browser storage, or static assets.
