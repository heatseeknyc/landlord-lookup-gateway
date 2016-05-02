The setup is slightly different for OS X; we don't maintain separate configuration files, but rather rely on some manual tweaking

uWSGI
-----

(1) Have a look at the init script 'bin/init-env-osx.rc' and make sure the settings make sense.  As deployed the file has settings specific to one particular laptop this was tested on, so in your environment things will be guaranteed to be at least slightly different; as you can see we have custom paths for Postgres and libssl includes, for example.  Either way the DYLD_FALLBACK_LIBRARY_PATH may need to be set so that these libraries can be found.  Also, ideally it shouldn't be setting any variables that aren't needed.  Again, just make sure it's tailored to your environment. 

(2) Once the files have been pushed, setup is analogous to the Ubuntu case:

  % cd /opt/uwsgi
  % source bin/init-env-osx.rc
  % which uwsgi
  /path/to/uwsgi
  % uwsgi --python-version
  3.4.3

The last step is crucial because it makes sure uWSGI is set up to find Python 3, not Python 2.  If you get an error message like:

  dyld: Library not loaded: libpython3.4m.dylib
  Referenced from: /path/to/bin/uwsgi
    Reason: image not found
    Trace/BPT trap: 5

That means your environment is only partially configurated to find Python 3 (it can find the executable, but not the libraries).  Again, look at the 'bin/init-env-osx.rc', which has a setting specifically to address this issue.



(3) Edit config/trivial.ini to override Ubuntu-specific uid/gid settings.

  uid = nobody 
  gid = staff 

As a glitch in our understanding of this process, for some reasons these settings don't seem to have the desired effect of setting the socket permissions to nobody.staff (as they do in the Ubuntu environment).  But that's OK, we can manually fix that after launching.  The main thing is to not leave the Ubuntu settings in there).

(4) Launch the trivial service (which will be slightly easier to ping and troubleshoot through the gateway than the actual REST services).

  uwsgi config/trivial.ini &

Check the output carefully for any warnings about permissions or stuff not found. 

(5) Check the perms on the socket we just deployed to.  If necessary, chmod them to the desierd uid/gid settings above. 

Now let's start nginx, and see if we can at least reach the HTML pages and the trivial service.



nginx
-----

As with uWSGI, our nginx service runs out of a specially created configuration dir (/opt/nginx), completely independent of the installed configuration root.    

(1) Set your PATH so that you can find nginx: 
  
  % cd /opt/nginx
  % source bin/init-env-nginx.rc 
  % which nginx
  /path/to/nginx

(2) Edit the server conf, and make sure we aren't running as the Ubuntu web user. 

  vi conf/nginx.conf
  
Change the line "user www-data" to "user nobody" or whatever your local default is. 

(3) Start the service, and make sure there are no complaints: 

  % sudo nginx -p /opt/nginx 

(4) Try a few test URLs:

  % bin/test-page-simple.sh
  % bin/test-endpoint-trivial.sh

The first should return a simple HTML page (that doesn't look like an error page).  The second should simply return the string "Woof!".  If it returns an error page (most like a "502 gateway error" string wrapped in an HTML page), you'll need to stop and troubleshoot.  Most likely it will turn out to be a permissions issue somewhere -- but whatever went wrong, most likely the REST services will suffer the same fate.

(5) Stop the service (just so we know how to): 

  % sudo nginx -p /opt/nginx -s stop


Start the 'hybrid' service
--------------------------

Exactly analogous as to the trivial service:

  % cd /opt/uwsgi
  % uwsgi config/hybrid.ini

As with the trivial service, we'll need to chmod the socket:

  % sudo chown nobody /tmp/uwsgi_hybrid.sock

Should now be reachable via nginx; let's try pinging the /lookup URL:

  bin/grab-endpoint-hybrid.sh 

Hopefully this won't yield a "502 gateway error".  If it says:

  {"error": "internal error"}

That's actually a good sign, because it means the endpoint is at least reachable.

But if successful, it should yield a response like this:

  {"extras": {"dhcr_active": false, "nychpd_contacts": 5, "taxbill": {"active_date": "2015-06-05", "owner_address": ["DAKOTA INC. (THE)", "1 W. 72ND ST.", "NEW YORK , NY 10023-3486"], "owner_name": "DAKOTA INC. (THE)"}}, "nycgeo": {"bbl": 1011250025, "bin": 1028637, "geo_lat": 40.77640230806594, "geo_lon": -73.97636507868083}}





