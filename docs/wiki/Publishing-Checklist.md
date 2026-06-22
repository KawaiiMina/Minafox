# Publishing Checklist

This checklist is for MinaFox's current standalone wrapper/profile and Arch package skeleton release phase. It prepares a release candidate for review; it does not authorize public publishing by itself.

## Approval gates

- [ ] Mina has explicitly approved public release preparation for the exact branch/commit.
- [ ] Mina has explicitly approved any public release action: push, tag, GitHub release, package upload, wiki publish, announcement, or website update.
- [ ] No checklist item is treated as approval by implication.

## Local validation

- [ ] Start from a clean, intentional worktree or record every expected local change.
- [ ] Run mobile harness tests:

```bash
python3 scripts/test-serve-minafox-mobile.py
```

- [ ] Run AI broker tests:

```bash
python3 scripts/test-minafox-ai-broker.py
```

- [ ] Run SearXNG validation:

```bash
python3 scripts/validate-minafox-searxng.py
```

- [ ] Run AI surface validation:

```bash
python3 scripts/validate-minafox-ai.py
```

- [ ] Run formatting/whitespace validation:

```bash
git diff --check
```

- [ ] Run Tick validation:

```bash
tick validate
```

## Package and wrapper validation

- [ ] Confirm the package still depends on distro `firefox`.
- [ ] Confirm the package does not provide or conflict with `firefox`.
- [ ] Confirm the package does not install a Firefox binary, Firefox source tree, or MinaFox-owned Firefox executable.
- [ ] Confirm installed payload paths remain wrapper/profile paths such as `/usr/share/minafox`, `/usr/share/doc/minafox`, `/usr/share/applications`, `/usr/share/icons`, `/usr/bin/minafox*`, and optional user systemd units.
- [ ] Confirm first launch syncs packaged assets into user-local MinaFox paths only.
- [ ] Confirm `minafox-update` refreshes installed profile/start-page assets and restarts only already-active or enabled optional services.
- [ ] Run package and updater validators when package files changed:

```bash
python3 scripts/validate-minafox-arch-package.py
python3 scripts/test-minafox-update.py
```

## Docs and wiki sync

- [ ] README links point to the current wiki mirror pages.
- [ ] `docs/wiki/Home.md` links to release notes, publishing checklist, troubleshooting, and known limitations.
- [ ] `docs/wiki/_Sidebar.md` includes release notes and publishing checklist.
- [ ] Install/update docs describe the wrapper/profile package without source-fork wording.
- [ ] Optional service docs state that services are installed but not auto-enabled.
- [ ] Privacy/licensing docs separate wrapper distribution from future Firefox ESR source-fork obligations.
- [ ] Troubleshooting docs include package, search, AI, LAN harness, static start-page, and Firefox-chrome CSS limits.
- [ ] Known limitations stay conservative and match the current package behavior.
- [ ] If publishing the GitHub wiki later, copy only reviewed `docs/wiki/*.md` content and preserve relative link intent.

## No-go checks

- [ ] No public-LAN exposure is documented as safe for the harness, SearXNG, or AI broker.
- [ ] No secrets, API keys, bearer tokens, cookies, local hostnames, private IP-only assumptions, or user-specific paths are embedded in static assets or docs.
- [ ] No release copy promises cloud provider chat, Hermes Gateway chat, or tool-calling chat for this release.
- [ ] No browser-side provider secrets are introduced.
- [ ] No copy implies MinaFox is affiliated with, endorsed by, or approved by Mozilla.
- [ ] No copy claims MinaFox is a compiled Firefox fork, browser engine, modified Firefox binary, Firefox replacement package, or source-distributed Firefox build in this phase.
- [ ] No package metadata claims `provides=('firefox')`, `conflicts=('firefox')`, or similar replacement behavior.

## Branch, commit, and tag preparation

- [ ] Review `git status --short` and separate release changes from unrelated local work.
- [ ] Review `git diff --check` and the final docs diff.
- [ ] Ensure Tick tasks for the release phase are completed or explicitly deferred.
- [ ] Prepare a release commit only after validation passes.
- [ ] Prepare tag text from [Release Notes](Release-Notes), but do not create the tag without explicit Mina approval.
- [ ] Prepare GitHub release text from [Release Notes](Release-Notes), but do not create a GitHub release without explicit Mina approval.

## Public publishing hold

- [ ] Do not push release branches unless Mina approves the exact push.
- [ ] Do not create or push tags unless Mina approves the exact tag.
- [ ] Do not create a GitHub release unless Mina approves the release title, body, tag, and target commit.
- [ ] Do not publish an Arch package, AUR update, wiki update, announcement, or website update unless Mina explicitly approves that channel.

## Evidence to keep

- [ ] Command output summary for local validation.
- [ ] Package/wrapper validation summary.
- [ ] Docs/wiki pages changed.
- [ ] Commit hash or branch name prepared for review.
- [ ] Explicit Mina approval reference before public publishing.
