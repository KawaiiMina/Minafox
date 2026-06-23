# MinaFox licensing and future source-fork guardrails

MinaFox is currently a wrapper/profile distribution around the operating-system Firefox package. This document keeps the current Arch package phase separate from any future Firefox ESR source-fork phase.

## Current wrapper/package phase

The current package is expected to remain MPL-safe because it:

1. does **not** bundle or install a modified Firefox binary;
2. does **not** copy Firefox source files into MinaFox-owned files without their original notices;
3. depends on the distro/system Firefox package (`firefox`) instead of replacing it or relicensing it;
4. ships MinaFox-owned launcher, profile, CSS, start page, policy, icon, helper, and documentation files separately;
5. keeps SearXNG as a separate optional localhost service/container, not as Firefox product code;
6. uses MinaFox branding and avoids implying Mozilla endorsement.

MinaFox-owned code and assets in this repository are licensed under MPL-2.0 where applicable in [`../LICENSE`](../LICENSE). Firefox remains provided by Mozilla/Arch through the system package, with its own notices and third-party licensing kept outside MinaFox-owned files. Third-party component notes live in [`../THIRD_PARTY_LICENSES.md`](../THIRD_PARTY_LICENSES.md).

## Arch package rule

`minafox-profile-git` should stay a profile/wrapper package until a deliberate source-fork package exists. It should:

- keep `depends=('firefox' ...)`;
- avoid `provides=('firefox')`, `conflicts=('firefox')`, or any package metadata that implies MinaFox replaces the system browser;
- avoid installing `/usr/bin/firefox`, `/usr/lib/firefox`, or a MinaFox-owned Firefox executable;
- install MinaFox files under `/usr/share/minafox`, `/usr/share/doc/minafox`, `/usr/share/applications`, `/usr/share/icons`, `/usr/bin/minafox*`, and optional user systemd units;
- keep the automatic first-run launcher sync user-local only; the explicit setup helper may ask for `sudo` to refresh Firefox enterprise policies under `/usr/lib/firefox/distribution`, but the package payload itself must not ship Firefox binaries/source there;
- keep the package description honest: “standalone Firefox profile wrapper”, not a compiled Firefox fork.

## Future Firefox ESR source-fork phase

A Firefox ESR source fork is legally possible under MPL-2.0, but it is a different phase with new release obligations.

Before distributing a modified Firefox build, MinaFox should:

1. preserve MPL and third-party notices in Firefox/MPL files;
2. keep modifications to existing MPL-covered files under MPL-2.0;
3. publish corresponding source or patch branches for distributed executables;
4. document how recipients can obtain that source;
5. avoid adding GPL-only or AGPL code directly into Firefox product source without a reviewed compatibility plan;
6. update about/license-style documentation and third-party notices;
7. avoid Mozilla/Firefox trademarks unless permission exists.

New MinaFox-only files added outside Firefox source may remain under MinaFox's chosen license. New files added inside a Firefox source tree should normally use MPL-2.0 unless there is a reviewed reason not to.

Until that source-fork phase exists, docs and package metadata should avoid calling MinaFox a Firefox build, Firefox distribution, rebranded Firefox binary, or Firefox replacement. Use "Firefox wrapper", "profile distribution", or "standalone wrapper" for the current release.
