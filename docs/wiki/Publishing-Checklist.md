# Publishing Checklist

This checklist is for release-channel readiness. Do not publish to a channel unless Mina explicitly approves that channel.

## Current approved public state

- Rc2 release copy is draft until the Git tag `v0.1.0-rc2` exists and Mina approves publishing.
- Current install guidance remains clone/package-skeleton based.
- MinaFox is described as a standalone wrapper/profile distribution.
- Firefox remains the distro `firefox` dependency.
- No docs should imply MinaFox bundles, compiles, relicenses, or replaces Firefox.

## Rc2 package-source gate

- [ ] Create/publish Git tag `v0.1.0-rc2` before public `makepkg -si` instructions are shared.
- [ ] Confirm `packaging/arch/minafox-profile-git/PKGBUILD` uses `source=("Minafox::git+https://github.com/KawaiiMina/Minafox.git#tag=${_minafox_source_ref}")` with `_minafox_source_ref='v0.1.0-rc2'`.
- [ ] Confirm `.SRCINFO` records `pkgver = 0.1.0rc2`, `pkgrel = 1`, and `source = Minafox::git+https://github.com/KawaiiMina/Minafox.git#tag=v0.1.0-rc2`.
- [ ] Confirm dynamic VCS `pkgver()` is absent for the rc2 path.
- [ ] Confirm public install commands check out `v0.1.0-rc2` before running `makepkg -si`.

## Before updating release docs

```bash
git status --short
git diff --check
python3 scripts/validate-minafox-standalone.py
python3 scripts/validate-minafox-arch-package.py
python3 scripts/validate-no-host-paths.py
python3 scripts/validate-no-firefox-telemetry.py
```

For full release validation, also run the test and validator list in [Development Guide](Development-Guide).

## Approval-gated channels

Do not do any of these without separate approval:

- push GitHub Wiki changes;
- upload AUR/package artifacts;
- upload release assets;
- sync the GitHub Wiki;
- publish website updates;
- post announcements;
- promote a release candidate to a stable release.

## GitHub Wiki sync candidate

The reviewed wiki mirror lives in `docs/wiki/*.md`. If Mina approves a GitHub Wiki update, sync only reviewed files from that directory and preserve relative wiki links such as `Getting-Started`, `Packaging-and-Updating`, and `Privacy-and-Licensing`.

Recommended sync scope after TASK-039:

- `Home.md`
- `_Sidebar.md`
- `_Footer.md`
- `Getting-Started.md`
- `Packaging-and-Updating.md`
- `Release-Notes.md`
- `Publishing-Checklist.md`
- `Services.md`
- `Mina-AI-Den.md`
- `MinaFox-Search.md`
- `Android-LAN-Testing.md`
- `Privacy-and-Licensing.md`
- `Known-Limitations.md`
- `Troubleshooting.md`
- `Architecture.md`
- `Repository-Map.md`
- `Development-Guide.md`
- `Brand-and-UX.md`
