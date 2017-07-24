#!/bin/sh -ue
kill -9 `cat track/hybrid.pid`
rm /tmp/uwsgi_hybrid.sock
