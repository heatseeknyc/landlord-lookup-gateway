#!/bin/sh -ue
uwsgi config/hybrid.ini &
sleep 1 
sudo chown nobody /tmp/uwsgi_hybrid.sock 
