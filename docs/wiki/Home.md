# MinaFox Wiki

MinaFox is a calm, private, kawaii Firefox wrapper for Arch/Hyprland. It uses the system Firefox binary underneath, then adds a dedicated MinaFox profile, launcher, desktop identity, pink/purple glass UI, local search, optional AI Den, and Android/LAN UX testing harness.

## What MinaFox is today

- **Standalone Firefox wrapper** — not a compiled Firefox fork yet.
- **Dedicated profile distribution** — profile prefs, chrome CSS, content CSS, start page, desktop entry, and icons.
- **Local-first browser companion** — optional SearXNG and AI broker stay loopback-first by default.
- **Kawaii glass UI experiment** — calm lavender/pink/purple workspace aesthetic with accessibility guardrails.
- **Arch-first package** — a `minafox-profile-git` package skeleton installs the launcher, assets, docs, and optional user services.

## Start here

- [Getting Started](Getting-Started) — install, first launch, and first checks.
- [Architecture](Architecture) — how the wrapper, profile, services, and start page fit together.
- [Services](Services) — systemd user units and service ports.
- [Android/LAN Testing](Android-LAN-Testing) — test responsive mobile UX without an APK.
- [Mina AI Den](Mina-AI-Den) — local broker, Ollama, provider modes, and safety boundaries.
- [MinaFox Search](MinaFox-Search) — local SearXNG overlay.
- [Packaging and Updating](Packaging-and-Updating) — Arch package and `minafox-update` behavior.
- [Release Notes](Release-Notes) — current public pre-release state.
- [Publishing Checklist](Publishing-Checklist) — approval-gated publishing and wiki sync notes.
- [Development Guide](Development-Guide) — file map, validation, and contribution workflow.
- [Privacy and Licensing](Privacy-and-Licensing) — telemetry posture, MPL wrapper phase, and source-fork guardrails.
- [Known Limitations](Known-Limitations) — current wrapper, service, and release-channel limits.
- [Troubleshooting](Troubleshooting) — common fixes.
- [Known Limitations](Known-Limitations) — conservative release limits.
- [Release Notes](Release-Notes) — draft notes for the current wrapper/package release phase.
- [Publishing Checklist](Publishing-Checklist) — pre-publish validation and approval gates.
- [Brand and UX](Brand-and-UX) — mascot, visual language, and UX rules.

## Repository at a glance

- `profile/` — Firefox prefs and chrome/content CSS.
- `desktop/` — start page and desktop launcher.
- `scripts/` — installers, launcher, updater, broker, harness, tests, validators.
- `searxng/` — SearXNG overlay and Compose config.
- `systemd/user/` — optional user services.
- `packaging/arch/minafox-profile-git/` — Arch package skeleton.
- `docs/` — versioned reference docs.

## Current limits

- MinaFox does not compile or ship Firefox source yet.
- The current public GitHub release is a pre-release, not a stable package channel.
- Firefox for Android does not support desktop `userChrome.css`; use the harness for mobile UX testing.
- Cloud AI providers are not implemented in the browser surface; secrets must never live in static assets.
- Hermes Gateway chat remains blocked until pairing/auth and tool-safety UX exist.
- Optional local services are not auto-enabled and are not public-LAN-safe by default.
