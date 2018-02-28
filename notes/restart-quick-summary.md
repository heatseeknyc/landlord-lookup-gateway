
Boiled down steps for server restart, based on the longer and more generalized "deploy and start services" writeup in this directory.

```
cd /opt/uwsgi/
source bin/init-env-python.rc 
which uwsgi
uwsgi --python-version
uwsgi config/trivial.ini &
uwsgi config/hybrid.ini &
cd /opt/nginx/
source bin/init-env-nginx.rc 
which nginx
nginx -v
```

So far, so good.  If the server has been rebooted you'll probably want to check if there's some other nginx process already running, and if so, deal with it appropriately:

```
ps -ef | grep nginx
kill -TERM whatever 
```

And to actually restart:

```
sudo nginx -p /opt/nginx -c conf/nginx.conf
```

