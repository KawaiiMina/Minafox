# MinaFox AI Provider Architecture

MinaFox AI is optional. The browser start page may show a calm **Mina AI Den**, but real provider calls should go through a future localhost-only broker instead of direct browser JavaScript.

## Design goals

- Keep browsing calm: the AI panel starts disabled and does not nag.
- Keep secrets out of static files: secrets must not be committed, stored in `desktop/start.html`, stored in `profile/user.js`, or placed in browser localStorage.
- Prefer local-first operation: Ollama is the first practical provider because it can run on `127.0.0.1`.
- Treat cloud providers clearly as Cloud mode.
- Treat Hermes Gateway clearly as LAN / advanced mode because Hermes Gateway can trigger tool-capable agents depending on the paired Hermes install.

## Provider modes

- Local: **Ollama** at `http://127.0.0.1:11434`.
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

This sprint only adds UI, documentation, and validation. There are no network calls and no provider secrets.
