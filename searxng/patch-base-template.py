#!/usr/bin/env python3
"""Patch SearXNG Simple base template to load MinaFox CSS after upstream CSS.

The upstream template chooses either sxng-ltr.min.css or sxng-rtl.min.css inside
an RTL conditional. Insert the MinaFox stylesheet after that conditional so both
LTR and RTL pages get the same late-loading design override.
"""
from __future__ import annotations

from pathlib import Path

BASE_TEMPLATE = Path("/usr/local/searxng/searx/templates/simple/base.html")
MINAFOX_LINK = (
    "  <link rel=\"stylesheet\" "
    "href=\"{{ url_for('static', filename='themes/simple/css/minafox.min.css') }}\" "
    "type=\"text/css\" media=\"screen\">"
)
ANCHOR = "  {% if get_setting('server.limiter') or get_setting('server.public_instance') %}"

text = BASE_TEMPLATE.read_text(encoding="utf-8")
if MINAFOX_LINK not in text:
    if ANCHOR not in text:
        raise SystemExit("Cannot patch SearXNG base.html: expected limiter/client CSS anchor not found")
    text = text.replace(ANCHOR, f"{MINAFOX_LINK}\n{ANCHOR}", 1)
    BASE_TEMPLATE.write_text(text, encoding="utf-8")
