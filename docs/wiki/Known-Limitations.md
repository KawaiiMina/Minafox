# Known Limitations

## Wrapper phase

MinaFox is currently a standalone Firefox wrapper/profile distribution. It configures and launches the operating-system Firefox package; it does not compile, bundle, replace, or relicense Firefox.

## Packaging

- Arch is the primary supported environment.
- The package skeleton is `minafox-profile-git`.
- Install guidance remains clone/package-skeleton based until a separate package channel is approved.
- `minafox-update` expects a local checkout and rebuilds/reinstalls from that checkout.

## Telemetry and privacy

MinaFox disables known Firefox telemetry/reporting surfaces through policies and profile prefs, but it does not remove Firefox source code paths from a compiled browser. Re-run the telemetry validator when Firefox or MinaFox prefs change.

## Search

MinaFox search is routed through local SearXNG. Upstream engine customization belongs in SearXNG configuration, not in direct browser-side integrations.

## AI Den

- Local Ollama chat is disabled unless explicitly enabled with `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1`.
- Cloud providers are metadata/detection-only.
- Hermes Gateway chat remains blocked until pairing/auth and tool-safety UX exist.
- Provider keys must not be stored in static browser assets or localStorage.

## Android and LAN testing

Firefox for Android does not load desktop `userChrome.css`. The current Android path is a LAN web harness for responsive UX testing, not a native Android browser build.

Only expose the harness on trusted LAN/Tailscale networks. Keep port `8766` blocked from untrusted networks.

## Future source fork

A Firefox ESR source fork is a later phase with separate source, licensing, packaging, and release obligations. Until that phase exists, use "Firefox wrapper", "profile distribution", or "standalone wrapper" for MinaFox.
