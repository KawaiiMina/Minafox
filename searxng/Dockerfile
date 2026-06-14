# MinaFox SearXNG overlay.
# The upstream image supplies the app; this layer adds MinaFox settings and a
# custom Simple-theme stylesheet. Keep this small so upstream SearXNG updates
# remain easy to absorb.
FROM docker.io/searxng/searxng:latest

COPY settings.yml /etc/searxng/settings.yml
COPY uwsgi.ini /etc/searxng/uwsgi.ini
COPY theme/minafox.css /usr/local/searxng/searx/static/themes/simple/css/minafox.min.css
# Use the upstream-compatible dark style name so current SearXNG accepts the
# settings value while the active dark style still follows MinaFox design.
COPY theme/minafox.css /usr/local/searxng/searx/static/themes/simple/css/dark.min.css
# Current SearXNG serves the Simple theme through bundled stylesheets rather
# than the legacy per-style CSS file. Append MinaFox overrides to the active
# bundled stylesheet files too, and add a dedicated late-loading CSS link to
# base.html so the visible search page actually inherits the cosmic fox
# glass/pink/lavender design even if upstream rebuilds bundled CSS on startup.
COPY theme/minafox.css /tmp/minafox.css
COPY theme/minafox-categories.js /usr/local/searxng/searx/static/themes/simple/js/minafox-categories.js
COPY patch-base-template.py /tmp/patch-base-template.py
RUN cat /tmp/minafox.css >> /usr/local/searxng/searx/static/themes/simple/sxng-ltr.min.css \
    && cat /tmp/minafox.css >> /usr/local/searxng/searx/static/themes/simple/sxng-rtl.min.css \
    && python3 /tmp/patch-base-template.py \
    && rm /tmp/minafox.css /tmp/patch-base-template.py
