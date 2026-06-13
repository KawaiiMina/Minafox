# MinaFox SearXNG overlay.
# The upstream image supplies the app; this layer adds MinaFox settings and a
# custom Simple-theme stylesheet. Keep this small so upstream SearXNG updates
# remain easy to absorb.
FROM docker.io/searxng/searxng:latest

COPY settings.yml /etc/searxng/settings.yml
COPY uwsgi.ini /etc/searxng/uwsgi.ini
COPY theme/minafox.css /usr/local/searxng/searx/static/themes/simple/css/minafox.min.css
