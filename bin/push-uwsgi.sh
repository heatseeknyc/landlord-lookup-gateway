#!/bin/sh -ue

DEST=/opt/uwsgi

rsync -avz uwsgi/bin $DEST
rsync -avz uwsgi/config $DEST
rsync -avz uwsgi/daemons $DEST
rsync -avz uwsgi/logs $DEST
rsync -avz uwsgi/pylib $DEST
rsync -avz uwsgi/tests $DEST


