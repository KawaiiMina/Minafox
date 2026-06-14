#!/usr/bin/env python3
"""Patch SearXNG Simple base template for MinaFox assets.

The upstream template chooses either sxng-ltr.min.css or sxng-rtl.min.css inside
an RTL conditional. Insert the MinaFox stylesheet after that conditional so both
LTR and RTL pages get the same late-loading design override. Also load the small
category guard script before </body> so the category checkboxes behave like a
single-choice tab bar.
"""
from __future__ import annotations

from pathlib import Path

BASE_TEMPLATE = Path("/usr/local/searxng/searx/templates/simple/base.html")
MINAFOX_LINK = (
    "  <link rel=\"stylesheet\" "
    "href=\"{{ url_for('static', filename='themes/simple/css/minafox.min.css') }}\" "
    "type=\"text/css\" media=\"screen\">"
)
MINAFOX_SCRIPT = (
    "  <script defer "
    "src=\"{{ url_for('static', filename='themes/simple/js/minafox-categories.js') }}\"></script>"
)
CSS_ANCHOR = "  {% if get_setting('server.limiter') or get_setting('server.public_instance') %}"
SCRIPT_ANCHOR = "</body>"

text = BASE_TEMPLATE.read_text(encoding="utf-8")
changed = False

if MINAFOX_LINK not in text:
    if CSS_ANCHOR not in text:
        raise SystemExit("Cannot patch SearXNG base.html: expected limiter/client CSS anchor not found")
    text = text.replace(CSS_ANCHOR, f"{MINAFOX_LINK}\n{CSS_ANCHOR}", 1)
    changed = True

if MINAFOX_SCRIPT not in text:
    if SCRIPT_ANCHOR not in text:
        raise SystemExit("Cannot patch SearXNG base.html: expected closing body anchor not found")
    text = text.replace(SCRIPT_ANCHOR, f"{MINAFOX_SCRIPT}\n{SCRIPT_ANCHOR}", 1)
    changed = True

if changed:
    BASE_TEMPLATE.write_text(text, encoding="utf-8")
