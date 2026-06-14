# Architecture

MinaFox is intentionally split into wrapper assets, local services, and optional development harnesses. The current phase avoids modifying or distributing Firefox itself.

## High-level system

```mermaid
flowchart TD
    User([User]) --> Launcher[minafox launcher]
    Launcher --> Firefox[System Firefox binary]
    Launcher --> Profile[(Dedicated MinaFox profile)]
    Profile --> ChromeCSS[userChrome.css]
    Profile --> ContentCSS[userContent.css]
    Profile --> StartPage[MinaFox start.html]
    StartPage --> Search{{MinaFox SearXNG<br>127.0.0.1:8888}}
    StartPage --> Broker{{Mina AI broker<br>127.0.0.1:8765}}
    Broker --> Ollama{{Ollama<br>127.0.0.1:11434}}
    Broker -. detection only .-> Hermes{{Hermes API Server<br>127.0.0.1:8642}}
    Android([Android browser]) --> Harness[MinaFox mobile harness<br>LAN/Tailscale :8766]
    Harness --> StartPage
```

## Components

- **Launcher** — `scripts/minafox-launcher.sh` wraps the system Firefox binary and ensures user-local assets are present.
- **Profile assets** — `profile/user.js`, `profile/userChrome.css`, and `profile/userContent.css` define prefs and UI styling.
- **Start page** — `desktop/start.html` is a static, local page with search, quick links, AI Den status, and service controls.
- **SearXNG overlay** — `searxng/` contains a local SearXNG container overlay bound to `127.0.0.1:8888`.
- **AI broker** — `scripts/minafox-ai-broker.py` exposes localhost discovery and local Ollama chat when explicitly enabled.
- **Android harness** — `scripts/serve-minafox-mobile.py` serves the start page and injects LAN service URLs for phone testing.
- **Package skeleton** — `packaging/arch/minafox-profile-git/` packages the wrapper without replacing Firefox.
- **User services** — `systemd/user/` contains optional service units for search, AI, and mobile harness.

## Desktop launch

```mermaid
sequenceDiagram
    participant User
    participant Launcher as minafox
    participant Firefox
    participant Profile as MinaFox profile
    participant Start as start.html
    User->>Launcher: run minafox
    Launcher->>Profile: sync packaged profile/start/assets if needed
    Launcher->>Firefox: start system firefox with MinaFox profile
    Firefox->>Start: load local start page
    Start-->>User: show dashboard/search/AI status
```

## Android test mode

```mermaid
sequenceDiagram
    participant Phone as Android browser
    participant Harness as mobile harness
    participant Start as start.html
    participant Search as LAN SearXNG
    participant Broker as LAN AI broker
    Phone->>Harness: GET http://desktop:8766/
    Harness->>Start: inject runtime config
    Start->>Search: call configured search URL
    Start->>Broker: call configured AI broker URL
```

## Design decisions

- Use the distro Firefox binary until the wrapper/package is reliable.
- Keep secrets out of static browser assets.
- Bind services to loopback by default unless LAN testing is explicit.
- Keep Android testing as a web harness instead of early Fenix/APK work.
- Make visual polish testable with validators, not just manual screenshots.
