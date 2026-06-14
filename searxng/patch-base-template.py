#!/usr/bin/env python3
"""Patch SearXNG Simple templates for MinaFox assets and polish.

The upstream base template chooses either sxng-ltr.min.css or sxng-rtl.min.css
inside an RTL conditional. Insert the MinaFox stylesheet after that conditional so
both LTR and RTL pages get the same late-loading design override. Also load the
small category guard script before </body> so the category checkboxes behave like
a single-choice tab bar.

The upstream categories template can render a hover/help bubble that says
"Click on the magnifier to perform search". MinaFox keeps the category rail calm
and icon-only, so remove that help node from the rendered template entirely.
"""
from __future__ import annotations

from pathlib import Path

BASE_TEMPLATE = Path("/usr/local/searxng/searx/templates/simple/base.html")
CATEGORIES_TEMPLATE = Path("/usr/local/searxng/searx/templates/simple/categories.html")
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
CATEGORY_HELP_LINE = (
    "            {%- if display_tooltip %}<div class=\"help\">"
    "{{ _('Click on the magnifier to perform search') }}</div>{% endif -%}\n"
)


def patch_base_template() -> bool:
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
    return changed


def patch_categories_template() -> bool:
    text = CATEGORIES_TEMPLATE.read_text(encoding="utf-8")
    if CATEGORY_HELP_LINE not in text:
        # Idempotent: already removed by a previous image build or upstream changed.
        return False
    CATEGORIES_TEMPLATE.write_text(text.replace(CATEGORY_HELP_LINE, "", 1), encoding="utf-8")
    return True


patch_base_template()
patch_categories_template()
