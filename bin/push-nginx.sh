#!/bin/sh -ue

DEST=/opt/nginx

rsync -avz nginx/conf $DEST
rsync -avz nginx/html $DEST
rsync -avz nginx/logs $DEST
rsync -avz nginx/bin $DEST


