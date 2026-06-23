# MinaFox Wrapper/Profile Release Copy

This page is the release-channel copy source for the current MinaFox standalone wrapper/profile release candidate. It is ready to adapt into a tag message, GitHub release body, wiki update summary, package/AUR note, or announcement draft after Mina explicitly approves that channel.

Do not publish, tag, upload, sync the public wiki, or announce from this page without separate explicit approval for the exact channel, title/body, tag, and target commit.

## Release title

MinaFox wrapper/profile release candidate

## Short channel summary

MinaFox is an Arch-first Firefox wrapper/profile package. It uses the distro `firefox` package underneath, then adds a dedicated MinaFox profile, launcher, desktop identity, local start page, pink/purple chrome CSS, local-first search configuration, optional Mina AI Den broker, optional SearXNG service support, optional Android/LAN UX harness, and release-readiness docs.

This release does not ship a modified Firefox binary, a Firefox source fork, a bundled browser engine, or a replacement for `/usr/bin/firefox`.

## GitHub release body draft

MinaFox is ready for review as a standalone wrapper/profile release candidate for Arch/Hyprland.

This release packages MinaFox-owned assets around the system Firefox package:

- `minafox` launcher for a dedicated MinaFox Firefox profile.
- Arch `minafox-profile-git` package skeleton.
- `minafox-update` helper for rebuilding from a checkout, refreshing installed profile/start-page assets, and restarting only MinaFox user services that are already active or enabled.
- MinaFox profile prefs, `userChrome.css`, `userContent.css`, desktop entry, icons, and static start page.
- Local SearXNG search configuration for `http://127.0.0.1:8888/search`.
- Optional Mina AI Den broker command and systemd user unit.
- Optional Android/LAN UX harness for trusted-network responsive and touch testing.
- Wiki documentation for install/update, package behavior, services, search, AI Den, Android/LAN testing, privacy/licensing, troubleshooting, known limitations, and publishing gates.

Install from a checkout on Arch:

```bash
git clone https://github.com/KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox/packaging/arch/minafox-profile-git
makepkg -si
```

If you already have the checkout, start from the existing `~/Minafox` path instead of cloning again.

Update an installed package from the checkout:

```bash
minafox-update
```

Useful update variants:

```bash
minafox-update --no-sync-profile-assets
minafox-update --no-restart-services
minafox-update --repo /path/to/Minafox
MINAFOX_REPO_DIR=/path/to/Minafox minafox-update
```

Optional services are installed as user units but are not auto-enabled. Enable them only when you want that local service:

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user enable --now minafox-ai-broker.service
systemctl --user enable --now minafox-mobile-harness.service
```

Service boundaries:

- `minafox-searxng.service` is local search support and should stay loopback-local by default.
- `minafox-ai-broker.service` defaults to `127.0.0.1:8765`; local Ollama chat requires explicit `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1`.
- `minafox-mobile-harness.service` is for trusted LAN/Tailscale phone testing. Do not expose it publicly.

Known limitations:

- MinaFox uses the distro `firefox` package. It does not bundle, replace, compile, provide, or conflict with Firefox.
- A future Firefox ESR source fork would be a separate phase with separate source, licensing, packaging, and release obligations.
- Non-Arch packages, Flatpak, Snap, AppImage, Windows, macOS, and Android APK packaging are not release targets here.
- Firefox chrome CSS can change across Firefox versions; the expected fallback is that Firefox still launches with the MinaFox profile and start page.
- The static start page cannot perform every privileged browser action directly.
- SearXNG, AI broker, and Android/LAN harness are optional and not auto-enabled.
- Cloud provider chat and Hermes Gateway chat are not available in this release; Hermes remains detection-only.
- No browser-side provider secrets ship in this release.

See [Known Limitations](Known-Limitations), [Packaging and Updating](Packaging-and-Updating), [Services](Services), [Mina AI Den](Mina-AI-Den), [Android/LAN Testing](Android-LAN-Testing), and [Privacy and Licensing](Privacy-and-Licensing) for the maintained release boundaries.

MinaFox is independent and is not affiliated with, endorsed by, or approved by Mozilla. Firefox is a Mozilla trademark. This release configures and launches the distro Firefox package with MinaFox-owned wrapper/profile assets; it is not a Firefox replacement package and does not claim browser-engine ownership.

## Tag message draft

```text
MinaFox wrapper/profile release candidate

Standalone Arch-first wrapper/profile release candidate for MinaFox.

This tag marks the release-copy/package-readiness state for the MinaFox wrapper phase:
- distro Firefox dependency, not a bundled or modified Firefox binary
- dedicated MinaFox profile, launcher, desktop identity, icons, prefs, CSS, and local start page
- Arch minafox-profile-git package skeleton and minafox-update helper
- optional SearXNG, AI broker, and Android/LAN harness user services, installed but not auto-enabled
- docs for install/update, services, privacy/licensing, troubleshooting, publishing gates, and known limitations

No public release action is implied by this message until Mina approves the exact tag, target commit, and channel publication.
```

## Wiki update summary draft

```text
Refresh MinaFox release-readiness wiki copy for the standalone wrapper/profile package phase.

The wiki now has channel-ready release notes, install/update commands, optional service boundaries, source-fork guardrails, Mozilla non-affiliation language, known limitations, and a publishing checklist that keeps tags, GitHub releases, package/AUR updates, wiki syncs, announcements, and website updates gated on explicit approval.
```

## Package or AUR note draft

```text
MinaFox packages as minafox-profile-git, a standalone Firefox profile/wrapper for Arch.

It depends on the distro firefox package and installs MinaFox launcher/profile/start-page assets, docs, icons, and optional user systemd units. It does not provide, conflict with, replace, bundle, or compile Firefox.

After install, run minafox to launch the MinaFox profile. Use minafox-update from a checkout to rebuild/reinstall, refresh packaged profile/start-page assets, reload user systemd units, and restart only MinaFox services that are already active or enabled.

Optional SearXNG, AI broker, and Android/LAN harness services are installed but not auto-enabled.
```

## Announcement draft

```text
MinaFox has a standalone wrapper/profile release candidate ready for review.

This is the Arch-first wrapper phase: it uses the system Firefox package and adds a dedicated MinaFox profile, launcher, local start page, desktop identity, pink/purple UI CSS, local-first search setup, optional AI Den broker, optional SearXNG support, optional Android/LAN UX harness, and release docs.

It is intentionally conservative. MinaFox does not ship a modified Firefox binary, does not bundle Firefox, does not replace /usr/bin/firefox, and is not a browser engine or Firefox source fork in this phase. Optional services are installed only as opt-in user services and are not auto-enabled.

Known limitations and publishing gates are documented in the wiki. MinaFox is independent and is not affiliated with, endorsed by, or approved by Mozilla.
```

## Maintained documentation links

- [Getting Started](Getting-Started) - install, first launch, and first checks.
- [Packaging and Updating](Packaging-and-Updating) - package intent, installed paths, first-launch asset sync, update command, and service restart policy.
- [Services](Services) - optional user services and default binds.
- [MinaFox Search](MinaFox-Search) - local SearXNG search layer.
- [Mina AI Den](Mina-AI-Den) - broker behavior, local Ollama opt-in, cloud-provider limits, and Hermes detection-only state.
- [Android/LAN Testing](Android-LAN-Testing) - trusted-network mobile harness.
- [Privacy and Licensing](Privacy-and-Licensing) and [`docs/licensing-and-source-fork.md`](../licensing-and-source-fork.md) - wrapper distribution and future source-fork guardrails.
- [Troubleshooting](Troubleshooting) - command, package, service, LAN, AI, search, update, and chrome-polish failure modes.
- [Known Limitations](Known-Limitations) - maintained limitations list.
- [Publishing Checklist](Publishing-Checklist) - validation, channel copy review, and approval gates.

## Release hold

This page drafts release-channel copy only. Do not create a tag, GitHub release, package/AUR update, wiki sync, announcement, website update, upload, or push from this page without explicit Mina approval for that action.
