#!/bin/sh -ue

DEST=/opt/nginx
UID=www-data
GID=www-data

rsync -avz nginx/conf $DEST
rsync -avz nginx/html $DEST
rsync -avz nginx/logs $DEST
rsync -avz nginx/bin $DEST

find $DEST | xargs chown $UID 
find $DEST | xargs chgrp $GID 


