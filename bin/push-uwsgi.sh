#!/bin/sh -ue

DEST=/opt/uwsgi
UID=www-data
GID=www-data

rsync -avz uwsgi/bin $DEST
rsync -avz uwsgi/config $DEST
rsync -avz uwsgi/daemons $DEST
rsync -avz uwsgi/logs $DEST
rsync -avz uwsgi/pylib $DEST
rsync -avz uwsgi/track $DEST

find $DEST | xargs chown $UID 
find $DEST | xargs chgrp $GID 

