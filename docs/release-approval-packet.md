# MinaFox Milestone 5 Approval Packet

This packet is for Mina's release decision on the current MinaFox standalone wrapper/profile release candidate. It does not publish, tag, upload, announce, sync wiki content, or change any release channel by itself.

## Decision requested

Approve, hold, or request fixes for the controlled wrapper release execution.

No public action should happen until Mina explicitly approves the exact branch, commit, tag name, release channel, and release copy for that channel.

## Frozen release candidate

- Branch: `agent/milestone-4-docs-release-readiness`
- Frozen commit: `394160a0f600ee26e6f74019c01d6f593046dd44`
- Release type: standalone wrapper/profile/package over distro Firefox
- Current package identity: `minafox-profile-git`
- Current package version from clean artifact: `0.1.0.r48.g394160a-1`

The frozen release candidate is not a compiled Firefox fork, bundled Firefox binary, replacement Firefox package, modified browser engine, or source-distributed Firefox build.

## Current local release-prep changes

The frozen package artifact and validation gate target commit `394160a0f600ee26e6f74019c01d6f593046dd44`.

Additional release-prep docs were drafted after that freeze and are currently local working-tree changes:

- `docs/wiki/Release-Notes.md`
- `docs/wiki/Publishing-Checklist.md`
- `docs/release-approval-packet.md`

These docs prepare release-channel copy and approval evidence. They do not change product behavior. If Mina wants these docs included in the public repository before release, they need a separate commit and push approval.

## Validation summary

Recommendation: GO for the release validation gate.

The reviewer ran the required gate from the frozen commit and then reran it after the concurrent release-copy docs appeared. All required checks passed:

```bash
python3 scripts/test-serve-minafox-mobile.py
python3 scripts/test-minafox-ai-broker.py
python3 scripts/validate-minafox-searxng.py
python3 scripts/validate-minafox-ai.py
python3 scripts/validate-no-host-paths.py
python3 scripts/validate-minafox-arch-package.py
python3 scripts/test-minafox-update.py
git diff --check
tick validate
```

Reviewer drift check:

- No behavior drift from Milestone 2, Milestone 3, or Milestone 4 claims.
- No new cloud, Hermes, or provider behavior.
- Ollama chat remains explicit opt-in.
- Cloud and Hermes remain unavailable for chat; Hermes remains metadata/detection-only.
- No public-LAN-safe claim was introduced.
- Source-fork wording remains clear: this release is a wrapper/profile around distro Firefox, with any future source fork treated as a separate phase.

## Package artifact summary

Clean artifact built from frozen commit `394160a0f600ee26e6f74019c01d6f593046dd44` in an isolated build root, not Mina's checkout.

- Artifact: `/tmp/minafox-task029-archbuild/artifacts/minafox-profile-git-0.1.0.r48.g394160a-1-any.pkg.tar.zst`
- SHA-256: `f6d7d371ec6a29628011b4ddafbe9ea3a1e2496109fe768312afa9799bcd52c8`
- Size: `1993896`
- Build log: `/tmp/minafox-task029-archbuild/logs/makepkg-final.log`
- Package metadata and payload log: `/tmp/minafox-task029-archbuild/logs/pacman-query.txt`

Package checks:

- Depends on distro `firefox`.
- Does not provide or conflict with `firefox`.
- Provides only `minafox-profile`.
- Conflicts only `minafox-profile`.
- Does not install `/usr/bin/firefox`, `/usr/lib/firefox`, `/usr/share/firefox`, `firefox-source`, or `mozilla-central`.
- Payload stays in expected wrapper/profile paths: `/usr/bin/minafox*`, `/usr/share/minafox`, `/usr/share/doc/minafox`, desktop entries, icons, licenses, and optional user systemd units.

Non-blocking caveat:

- An optional disposable install smoke pulled full Firefox dependencies in a throwaway Arch container before cleanup was interrupted. The worker reported transient container `badf159b0c2e` may still be running. The leader session could not inspect Docker due daemon socket permissions and did not restart Docker because unrelated user containers may be active.

## Release copy to approve

Release title:

```text
MinaFox wrapper/profile release candidate
```

Short channel summary:

```text
MinaFox is an Arch-first Firefox wrapper/profile package. It uses the distro firefox package underneath, then adds a dedicated MinaFox profile, launcher, desktop identity, local start page, pink/purple chrome CSS, local-first search configuration, optional Mina AI Den broker, optional SearXNG service support, optional Android/LAN UX harness, and release-readiness docs.

This release does not ship a modified Firefox binary, a Firefox source fork, a bundled browser engine, or a replacement for /usr/bin/firefox.
```

Prepared channel copy is in `docs/wiki/Release-Notes.md`:

- GitHub release body draft
- Tag message draft
- Wiki update summary draft
- Package/AUR note draft
- Announcement draft

Publishing gates and copy review checks are in `docs/wiki/Publishing-Checklist.md`.

Exact channel drafts for approval:

```text
GitHub release body

MinaFox is ready for review as a standalone wrapper/profile release candidate for Arch/Hyprland.

This release packages MinaFox-owned assets around the system Firefox package:

- minafox launcher for a dedicated MinaFox Firefox profile.
- Arch minafox-profile-git package skeleton.
- minafox-update helper for rebuilding from a checkout, refreshing installed profile/start-page assets, and restarting only MinaFox user services that are already active or enabled.
- MinaFox profile prefs, userChrome.css, userContent.css, desktop entry, icons, and static start page.
- Local SearXNG search configuration for http://127.0.0.1:8888/search.
- Optional Mina AI Den broker command and systemd user unit.
- Optional Android/LAN UX harness for trusted-network responsive and touch testing.
- Wiki documentation for install/update, package behavior, services, search, AI Den, Android/LAN testing, privacy/licensing, troubleshooting, known limitations, and publishing gates.

Install from a checkout on Arch:

git clone https://github.com/KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox/packaging/arch/minafox-profile-git
makepkg -si

If you already have the checkout, start from the existing ~/Minafox path instead of cloning again.

Update an installed package from the checkout:

minafox-update

Useful update variants:

minafox-update --no-sync-profile-assets
minafox-update --no-restart-services
minafox-update --repo /path/to/Minafox
MINAFOX_REPO_DIR=/path/to/Minafox minafox-update

Optional services are installed as user units but are not auto-enabled. Enable them only when you want that local service:

/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user enable --now minafox-ai-broker.service
systemctl --user enable --now minafox-mobile-harness.service

Service boundaries:

- minafox-searxng.service is local search support and should stay loopback-local by default.
- minafox-ai-broker.service defaults to 127.0.0.1:8765; local Ollama chat requires explicit MINAFOX_AI_ENABLE_OLLAMA_CHAT=1.
- minafox-mobile-harness.service is for trusted LAN/Tailscale phone testing. Do not expose it publicly.

Known limitations:

- MinaFox uses the distro firefox package. It does not bundle, replace, compile, provide, or conflict with Firefox.
- A future Firefox ESR source fork would be a separate phase with separate source, licensing, packaging, and release obligations.
- Non-Arch packages, Flatpak, Snap, AppImage, Windows, macOS, and Android APK packaging are not release targets here.
- Firefox chrome CSS can change across Firefox versions; the expected fallback is that Firefox still launches with the MinaFox profile and start page.
- The static start page cannot perform every privileged browser action directly.
- SearXNG, AI broker, and Android/LAN harness are optional and not auto-enabled.
- Cloud provider chat and Hermes Gateway chat are not available in this release; Hermes remains detection-only.
- No browser-side provider secrets ship in this release.

See Known Limitations (https://github.com/KawaiiMina/Minafox/blob/v0.1.0-rc1/docs/wiki/Known-Limitations.md), Packaging and Updating (https://github.com/KawaiiMina/Minafox/blob/v0.1.0-rc1/docs/wiki/Packaging-and-Updating.md), Services (https://github.com/KawaiiMina/Minafox/blob/v0.1.0-rc1/docs/wiki/Services.md), Mina AI Den (https://github.com/KawaiiMina/Minafox/blob/v0.1.0-rc1/docs/wiki/Mina-AI-Den.md), Android/LAN Testing (https://github.com/KawaiiMina/Minafox/blob/v0.1.0-rc1/docs/wiki/Android-LAN-Testing.md), and Privacy and Licensing (https://github.com/KawaiiMina/Minafox/blob/v0.1.0-rc1/docs/wiki/Privacy-and-Licensing.md) for the maintained release boundaries.

MinaFox is independent and is not affiliated with, endorsed by, or approved by Mozilla. Firefox is a Mozilla trademark. This release configures and launches the distro Firefox package with MinaFox-owned wrapper/profile assets; it is not a Firefox replacement package and does not claim browser-engine ownership.

Tag message

MinaFox wrapper/profile release candidate

Standalone Arch-first wrapper/profile release candidate for MinaFox.

This tag marks the release-copy/package-readiness state for the MinaFox wrapper phase:
- distro Firefox dependency, not a bundled or modified Firefox binary
- dedicated MinaFox profile, launcher, desktop identity, icons, prefs, CSS, and local start page
- Arch minafox-profile-git package skeleton and minafox-update helper
- optional SearXNG, AI broker, and Android/LAN harness user services, installed but not auto-enabled
- docs for install/update, services, privacy/licensing, troubleshooting, publishing gates, and known limitations

No public release action is implied by this message until Mina approves the exact tag, target commit, and channel publication.

Wiki update summary

Refresh MinaFox release-readiness wiki copy for the standalone wrapper/profile package phase.

The wiki now has channel-ready release notes, install/update commands, optional service boundaries, source-fork guardrails, Mozilla non-affiliation language, known limitations, and a publishing checklist that keeps tags, GitHub releases, package/AUR updates, wiki syncs, announcements, and website updates gated on explicit approval.

Package or AUR note

MinaFox packages as minafox-profile-git, a standalone Firefox profile/wrapper for Arch.

It depends on the distro firefox package and installs MinaFox launcher/profile/start-page assets, docs, icons, and optional user systemd units. It does not provide, conflict with, replace, bundle, or compile Firefox.

After install, run minafox to launch the MinaFox profile. Use minafox-update from a checkout to rebuild/reinstall, refresh packaged profile/start-page assets, reload user systemd units, and restart only MinaFox services that are already active or enabled.

Optional SearXNG, AI broker, and Android/LAN harness services are installed but not auto-enabled.

Announcement

MinaFox has a standalone wrapper/profile release candidate ready for review.

This is the Arch-first wrapper phase: it uses the system Firefox package and adds a dedicated MinaFox profile, launcher, local start page, desktop identity, pink/purple UI CSS, local-first search setup, optional AI Den broker, optional SearXNG support, optional Android/LAN UX harness, and release docs.

It is intentionally conservative. MinaFox does not ship a modified Firefox binary, does not bundle Firefox, does not replace /usr/bin/firefox, and is not a browser engine or Firefox source fork in this phase. Optional services are installed only as opt-in user services and are not auto-enabled.

Known limitations and publishing gates are documented in the wiki. MinaFox is independent and is not affiliated with, endorsed by, or approved by Mozilla.
```

## Proposed release channels

Mina can approve any subset of these channels:

- Commit and push the local release-prep docs to `agent/milestone-4-docs-release-readiness`.
- Create and push a release tag targeting `394160a0f600ee26e6f74019c01d6f593046dd44`.
- Create a GitHub release using the approved title/body and tag.
- Publish or attach the clean Arch package artifact.
- Sync reviewed `docs/wiki/*.md` content to the GitHub wiki.
- Publish an AUR/package note based on the approved package copy.
- Publish an announcement based on the approved announcement draft.

Recommended conservative first release path:

1. Approve committing/pushing the release-prep docs.
2. Approve a tag name and target commit.
3. Approve a GitHub release body as an early wrapper/profile release candidate.
4. Hold public AUR/package publication until Mina explicitly wants that channel.

Suggested tag name if Mina wants one:

```text
v0.1.0-rc1
```

Suggested GitHub release state:

```text
Pre-release
```

## Known limitations and risks

- MinaFox uses the distro `firefox` package. It does not bundle, replace, compile, provide, or conflict with Firefox.
- A future Firefox ESR source fork would be a separate project phase with separate source, licensing, packaging, and release obligations.
- Non-Arch packages, Flatpak, Snap, AppImage, Windows, macOS, and Android APK packaging are not release targets here.
- Firefox chrome CSS can change across Firefox versions; the expected fallback is that Firefox still launches with the MinaFox profile and start page.
- The static start page cannot perform every privileged browser action directly.
- SearXNG, AI broker, and Android/LAN harness services are optional and not auto-enabled.
- Cloud provider chat and Hermes Gateway chat are not available in this release; Hermes remains detection-only.
- No browser-side provider secrets ship in this release.
- Public-LAN exposure remains a no-go for the mobile harness, SearXNG, and AI broker.
- MinaFox is independent and is not affiliated with, endorsed by, or approved by Mozilla. Firefox is a Mozilla trademark.
- Docker cleanup for one reported throwaway packaging container could not be verified from the leader session due local daemon permissions.

## Approval options

Mina can answer with one of these:

- Approve all proposed first-release steps: commit/push release-prep docs, create tag `v0.1.0-rc1` at `394160a0f600ee26e6f74019c01d6f593046dd44`, create a GitHub pre-release, and keep AUR/package/wiki/announcement channels held unless separately approved.
- Approve selected channels only, naming the exact channels and any changed tag/title/body text.
- Hold release action and keep the current branch/artifact as an internal release candidate.
- Request fixes, naming the docs, package, validation, or copy changes required before another approval packet.

Any approval should name the exact branch, target commit, tag if any, release title/body source, and channels approved.
