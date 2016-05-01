#!/bin/sh -ue

UWSGI_ROOT=/opt/uwsgi
NGINX_ROOT=/opt/nginx

rsync -avz tests $USWGI_ROOT
rsync -avz pylib $USWGI_ROOT
rsync -avz daemons $USWGI_ROOT
rsync -avz config $USWGI_ROOT


