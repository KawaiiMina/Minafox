# Third-party licenses and compliance notes

MinaFox currently ships as a Firefox profile/wrapper distribution. This file tracks the external components MinaFox depends on or interoperates with so licensing stays explicit as the project grows.

## MinaFox-owned code

- **License:** MPL-2.0, see [`LICENSE`](LICENSE).
- **Scope:** launcher scripts, profile templates, start page, validators, MinaFox CSS/JS, documentation, icons, packaging skeleton, and optional local helper scripts maintained in this repository.

## System Firefox

- **Role:** runtime dependency provided by the operating-system package manager.
- **Arch package dependency:** `firefox`.
- **License:** Mozilla Public License 2.0 and other notices distributed by Mozilla/Arch with Firefox.
- **MinaFox handling:** MinaFox does not bundle a Firefox executable, does not copy Firefox source files into MinaFox-owned files, and does not claim Mozilla endorsement. It launches the system `firefox` binary with a MinaFox profile and user-local assets.

## SearXNG

- **Role:** optional localhost private search service, normally run from an upstream container image with a MinaFox overlay.
- **License:** SearXNG is AGPL-3.0-or-later upstream. Keep SearXNG service/container compliance separate from Firefox/MPL compliance.
- **MinaFox handling:** MinaFox ships configuration, a Dockerfile, and MinaFox-owned overlay CSS/JS/template patching for a local service. It is not linked into Firefox or copied into Firefox product source.

## Docker / Podman / Compose

- **Role:** optional local runtime for SearXNG.
- **MinaFox handling:** optional dependencies only; MinaFox does not vendor these tools.

## Ollama and AI providers

- **Role:** optional Mina AI Den providers accessed through a localhost-only broker.
- **MinaFox handling:** MinaFox does not vendor Ollama or cloud-provider SDKs in the static page. Provider API keys must remain in user-local environment/config/keyring material, never committed to this repo.

## Firefox extensions

- **Role:** optional user-installed extensions.
- **MinaFox handling:** MinaFox policies allow user-installed extensions but should not force-install bundled extension code by default. If bundled/forced extensions are added later, document each extension's license and source/notice requirements here.

## Future Firefox ESR source fork

If MinaFox starts distributing a modified Firefox build, update this file before release with:

1. the exact Firefox upstream source/revision,
2. where recipients can obtain the corresponding source for MPL-covered files,
3. a list of modified MPL-covered files or patch branches,
4. preserved Mozilla and third-party notices,
5. any new third-party code added to the browser source tree,
6. trademark/branding notes confirming the build is independent from Mozilla unless written permission exists.
