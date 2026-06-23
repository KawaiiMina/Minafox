# Known Limitations

This page records conservative release limits for the current standalone MinaFox wrapper/profile distribution.

## Firefox wrapper boundary

MinaFox uses the distro `firefox` package. It does not bundle Firefox, replace `/usr/bin/firefox`, provide or conflict with the Firefox package, compile Firefox, or ship a modified Firefox binary.

A future Firefox ESR source fork would be a separate phase with separate source, licensing, packaging, and release obligations. See [Privacy and Licensing](Privacy-and-Licensing) and [`docs/licensing-and-source-fork.md`](../licensing-and-source-fork.md).

## Arch-first packaging

The validated package path is the Arch `minafox-profile-git` wrapper/profile package. Other distros, Flatpak, Snap, AppImage, Windows, macOS, and Android APK packaging are not release targets here.

The package installs optional user services, but it does not auto-enable them.

## Firefox-version-sensitive chrome

`userChrome.css` and `userContent.css` style the distro Firefox UI and content surfaces. Firefox updates can change internal chrome selectors, so small toolbar, tab, sidebar, or spacing differences can appear between Firefox versions.

The expected fallback is that Firefox still launches with the MinaFox profile and start page. Chrome polish regressions should be handled as CSS follow-up work after validating the affected Firefox version.

## Static start-page privilege limits

`desktop/start.html` is a static local page. Firefox does not let that page perform every privileged browser action directly. Settings/Profile controls therefore copy or display `about:` commands such as `about:preferences` and `about:profiles` when direct navigation is blocked.

This is intentional fallback behavior, not a broken settings integration.

## Local search limits

MinaFox search points to local SearXNG at `http://127.0.0.1:8888/search` by default. Upstream engines are configured through SearXNG, not separate browser-side integrations.

SearXNG is optional, local-first, and not auto-enabled. If the service is offline, the start page should fail calmly instead of silently sending searches to a public fallback engine.

Do not expose SearXNG publicly as part of this release.

## AI Den limits

Mina AI Den talks to the local MinaFox broker at `127.0.0.1:8765` by default. The broker is optional and not auto-enabled.

Local Ollama chat is disabled unless `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1` is set explicitly and Ollama is reachable. Cloud providers are metadata-only in this release, and no browser-side provider secrets or cloud chat flow ships here.

Hermes Gateway is detection-only until pairing/auth, secrets storage, and tool-safety UX are designed and implemented.

## Android and LAN limits

The Android/LAN harness is a trusted-network testing tool for responsive UX. It is not a public web service and is not a native Android browser build.

Firefox for Android does not load the desktop `userChrome.css` wrapper. Use the harness to test the start page, touch behavior, and service URLs from a phone, but do not treat it as feature parity with a future Android app.

Only use LAN bindings on trusted LAN/Tailscale networks. There is no public-LAN-safe-by-default claim for the harness, SearXNG, or AI broker.

## Telemetry limit

MinaFox disables Firefox telemetry/reporting through policies and profile prefs. In the wrapper phase, this configures the distro Firefox binary; it does not remove code from Firefox source.

## Update and customization limits

`minafox-update` refreshes packaged profile/start-page assets by default and restarts only services that are already active or enabled. It does not start inactive+disabled optional services.

Local profile/start-page customizations can be preserved with `minafox-update --no-sync-profile-assets`, but then packaged UI/profile changes will not be copied into the local profile until sync is re-enabled.

See [Troubleshooting](Troubleshooting), [Packaging and Updating](Packaging-and-Updating), and [Services](Services) for practical commands.
