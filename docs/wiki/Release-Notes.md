# Release Notes

These notes describe the current Milestone 4 release-readiness phase for MinaFox's standalone wrapper/profile distribution. They are draft notes for review before any public release action.

## Release phase

MinaFox is currently a wrapper/profile/package around the distro Firefox package. It uses the system `firefox` binary and adds MinaFox-owned launcher scripts, a dedicated profile namespace, UI CSS, a local start page, optional local services, icons, desktop integration, docs, and Arch package skeleton.

This phase does not compile Firefox, bundle a Firefox binary, replace `/usr/bin/firefox`, provide or conflict with the distro `firefox` package, or ship a modified browser engine.

## What is included

- `minafox` launcher for the dedicated MinaFox Firefox profile.
- Arch `minafox-profile-git` package skeleton for wrapper/profile installation.
- `minafox-update` helper for rebuilding from a checkout, refreshing installed profile/start-page assets, and restarting only already-active or enabled MinaFox user services.
- MinaFox profile prefs, `userChrome.css`, `userContent.css`, desktop entry, icons, and static start page.
- Local SearXNG search configuration that points MinaFox search to `http://127.0.0.1:8888/search` by default.
- Optional Mina AI Den broker installed as a command and systemd user unit.
- Optional Android/LAN UX harness for responsive and touch testing from a trusted phone or LAN device.
- Wiki documentation for install/update, package behavior, optional services, Android/LAN testing, local search, AI Den boundaries, privacy/licensing, troubleshooting, and known limitations.

## Documentation outcomes

Milestone 4 documentation now covers the release surface from installation through pre-publish review:

- [Getting Started](Getting-Started) explains clone installs, Arch package installs, first launch, and first checks.
- [Packaging and Updating](Packaging-and-Updating) documents the Arch package skeleton, installed paths, first-launch asset sync, `minafox-update`, and service restart policy.
- [Services](Services) documents optional user services and their default binds.
- [MinaFox Search](MinaFox-Search) documents the local SearXNG search layer.
- [Mina AI Den](Mina-AI-Den) documents the broker, local Ollama opt-in, cloud-provider limits, and Hermes detection-only state.
- [Android/LAN Testing](Android-LAN-Testing) documents the trusted-network mobile harness and Android diagnostics.
- [Privacy and Licensing](Privacy-and-Licensing) and [`docs/licensing-and-source-fork.md`](../licensing-and-source-fork.md) separate the current wrapper phase from any future Firefox source-fork phase.
- [Troubleshooting](Troubleshooting) covers command, package, service, LAN, AI, search, update, and chrome-polish failure modes.
- [Known Limitations](Known-Limitations) records conservative release boundaries.
- [Publishing Checklist](Publishing-Checklist) defines local validation, package/wrapper validation, docs/wiki sync, branch/commit/tag preparation, and Mina approval gates.

## Optional service boundaries

The Arch package installs optional service units, but it does not auto-enable them.

- `minafox-searxng.service` is a local search service and should stay loopback-local by default.
- `minafox-ai-broker.service` defaults to `127.0.0.1:8765`; local Ollama chat requires explicit `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1`.
- `minafox-mobile-harness.service` binds for phone testing and is trusted-network-only. Do not expose it through public router rules, public reverse proxies, or untrusted LANs.

Cloud provider chat and Hermes Gateway chat are not available in this release. Hermes remains detection-only until pairing/auth, secrets storage, and tool-safety UX exist.

## Privacy, licensing, and affiliation

MinaFox disables Firefox telemetry/reporting through enterprise policies and profile prefs in the wrapper phase. This configures the distro Firefox binary; it does not remove telemetry code paths from Firefox source.

MinaFox-owned code is MPL-2.0. The current package keeps MinaFox-owned assets and helpers separate from Firefox source and depends on the distro `firefox` package.

MinaFox is independent and is not affiliated with or endorsed by Mozilla. Release copy should avoid implying Mozilla approval, Firefox replacement status, or browser-engine ownership.

## Known limitations

- No modified Firefox binary ships in this phase.
- No Firefox source fork is distributed in this phase.
- Non-Arch packages are not release targets here.
- Firefox chrome CSS can be sensitive to distro Firefox version changes.
- The static start page cannot perform every privileged browser action directly.
- SearXNG, AI broker, and Android/LAN harness are optional and not auto-enabled.
- Public-LAN exposure is a no-go for this release.
- Browser-side provider secrets are a no-go for this release.
- Cloud/Hermes chat promises are a no-go for this release.

See [Known Limitations](Known-Limitations) for the maintained limitations list.

## Pre-publish status

These notes are a draft. Do not publish a public release, tag, package, wiki update, or GitHub release from this checklist without explicit Mina approval.
