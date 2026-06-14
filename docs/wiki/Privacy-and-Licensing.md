# Privacy and Licensing

## Privacy posture

MinaFox disables Firefox telemetry/reporting at both the policy and profile layers.

### Enterprise policies

`distribution/policies.json` covers telemetry shutdown, Firefox studies shutdown, default browser agent shutdown, feedback/screenshot/background integrations where policy-supported, and locked telemetry prefs.

### Profile prefs

`profile/user.js` disables or reduces toolkit telemetry, health report/data submission, crash auto-submission, Normandy/Shield/experiments, Activity Stream telemetry and sponsored content, browser ping-centre telemetry, search/urlbar event telemetry, Quick Suggest data collection, captive portal/connectivity probes, and private attribution submission.

Validate:

```bash
python3 scripts/validate-no-firefox-telemetry.py
```

## Limits

This is not a Firefox source-code removal. MinaFox currently configures and wraps the distro Firefox binary; it does not physically remove telemetry code paths from a compiled Firefox build.

## Licensing

MinaFox-owned code is MPL-2.0. See `LICENSE`.

The wrapper phase remains separate from Firefox source:

- no modified Firefox binary is bundled;
- no Firefox source files are copied into MinaFox-owned files;
- the package depends on system `firefox`;
- MinaFox ships separate launcher/profile/CSS/start-page/policy/icon/helper files;
- SearXNG is an optional separate localhost service/container;
- MinaFox branding does not imply Mozilla endorsement.

Third-party notes live in `THIRD_PARTY_LICENSES.md`.

## Trademarks and brand use

Brand-usage rules live in `BRANDING.md`. In short: the code license does not grant permission to use the MinaFox name, logo, or mascot for modified builds that look like official MinaFox builds, and Firefox is a trademark of Mozilla Foundation. MinaFox is independent and is not affiliated with or endorsed by Mozilla.

## Future source-fork guardrails

Before distributing a modified Firefox build, MinaFox must preserve MPL and third-party notices, keep MPL-covered file modifications under MPL-2.0, publish corresponding source or patch branches, document source availability, avoid incompatible code additions, update license/about documentation, and avoid Mozilla/Firefox trademarks unless permission exists.
