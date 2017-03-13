Startup instructions for uWSGI + nginx, out of the box.  To some extent, these are Ubuntu-centric, but basically work on OS X also with some caveats + tweaking (which we've attempted to make special note of). 


Deployment
----------

"Deployment", as such, means simply pushing the 2 source trees into their local deployment locations.  These are configurable, but the suggested locations (and the ones enabled by default) are::

  /opt/uwsgi
  /opt/nginx

The directories will need to be created if they weren't present already (and ideally, they should be empty at the time the pushing scripts are invoked).  These in turn live in the ``bin`` dir up and over from here::

  ../bin/push-uwsgi.sh
  ../bin/push-ngins.sh


uWSGI config
------------

Once things have been pushed, go to the deployment location::

  cd /opt/uwsgi

And notice that the file tree looks a lot like the ``uwsgi`` dir out of the repo.  At this point few environment variables are needed to run the test scripts.  If you're in an Ubuntu environment, you'll just need to run the script::

  bin/init-env-python.rc

If you're building on OS X (where various dependencies tend to have different locations) have a look at the init script 'bin/init-env-osx.rc' and make sure the settings make sense.  As deployed the file has settings specific to one particular laptop this was tested on, so in your environment things will be guaranteed to be at least slightly different; as you can see we have custom paths for Postgres and libssl includes, for example.  Either way the DYLD_FALLBACK_LIBRARY_PATH may need to be set so that these libraries can be found.  Also, ideally it shouldn't be setting any variables that aren't needed.  Again, just make sure it's tailored to your environment. 

(2) Once the files have been pushed, do some basic sanity checks on your setup::

  which uwsgi
  /path/to/uwsgi
  uwsgi --python-version
  3.4.3

The last step is crucial because it makes sure uWSGI is set up to find Python 3, not Python 2.  If you get an error message like::

  dyld: Library not loaded: libpython3.4m.dylib
  Referenced from: /path/to/bin/uwsgi
    Reason: image not found
    Trace/BPT trap: 5

That means your environment is only partially configurated to find Python 3 (it can find the executable, but not the libraries).  Again, look at the 'bin/init-env-osx.rc', which has a setting specifically to address this issue.

(3) Edit configuration the following configuraiton files to reflect proper credentials and defaults::

  cd /opt/uwsgi
  vi config/postgres.json
  vi config/nycgeo-live.json 

For the ``postgres`` config, make sure the ``readuser`` password is set, and that the ``database`` points to the database instance we just installed to.  For the ``nycgeo-live`` config, you'll need to supply your NYGGeoclient API key + id. 

(3b) (OS X) Edit both gateway config files::

  cd /opt/uwsgi
  % vi config/trivial.ini 
  % vi config/hybrid.ini 

to override Ubuntu-specific uid/gid settings::

  uid = nobody 
  gid = wheel 

For some reasons these settings don't seem to have the desired effect of setting the socket permissions to nobody.staff (as they do in the Ubuntu environment).  But that's OK, we can manually fix that after launching.  The main thing is to not leave the Ubuntu settings in there).


Flask services
--------------

(4) Run the (pure-flask) test daemons + smoketest scripts, both with and without the --mock flag::

  source bin/launch-test-daemons.rc

These should launch quietly.  At this point it'd be highly desirable to make sure you can ping the services at the "pure flask" level.  First we can try pinging them with the --mock directive::

  python3 tests/test-nycgeo.py --mock
  python3 tests/test-hybrid.py --mock

And if you're able to run "live" Flask services, you can try these tests, which will ping the Geoclient API::

  python3 tests/test-nycgeo.py 
  python3 tests/test-hybrid.py

And make sure the respond reasonably -- basically the output for each of these scripts should be pure JSON structs (with no warnings exception traces), to STDOUT only; and the JSON structs themselves should contain no nested fields which look like error messages.

[TODO: provide separate writeup about verifying output].


uWSGI wrappers
--------------

(5) Make sure there are no pre-existing domain sockets from previous installation attempts::

  ls -lctd /tmp/uwsgi_*

If any do exist, it's best to delete them.

(6) Launch the both the 'hybrid' and 'trivial' services.  The 'hybrid' service is what runs the actual gateway, but the trivial service will be slightly easier to troubleshoot.::

  uwsgi config/trivial.ini &
  uwsgi config/hybrid.ini &

Check the output carefully for any warnings about permissions or stuff not found.  When things are going smoothly, it should look something like this (though the numbers on the top line may differ)::

  [4] 82564
  [uWSGI] getting INI configuration from config/trivial.ini

And similarly for the hybrid service.

(7) Check the perms on the socket we just deployed to (which will now show up as the sole file available under the glob used up above)::

  ls -lctd /tmp/uwsgi_*

If necessary, chmod them to the desired uid/gid settings above.

Now let's start nginx, and see if we can at least reach the HTML pages and the trivial service.


nginx
-----

As with uWSGI, our nginx service runs out of a specially created configuration dir (/opt/nginx), completely independent of the installed configuration root.    

(0) Make sure no other nginx services are running (due to an earlier installation or default system configuration).

(1) Set your PATH so that you can find nginx::
  
  % cd /opt/nginx
  source bin/init-env-nginx.rc 
  % which nginx
  /path/to/nginx

(2) (OS X) Edit the server conf, and make sure we aren't running as the Ubuntu web user::

  % vi conf/nginx.conf
  
Change the line "user www-data" to "user nobody" or whatever your local default is.

(3) Start the service, and make sure there are no complaints::

  % sudo nginx -p /opt/nginx 

NOTE: That's for a more modern nginx (1.9+).  For older versions (1.4-ish), you'll need to specify the configuration more explicitly::

  % sudo nginx -p /opt/nginx -c conf/nginx.conf

BTW, if you want you can try stopping the service at this point, just so you know how::

  % sudo nginx -p /opt/nginx -s stop

And then restarting per the cues above. 

(4) Try a few test URLs::

  % cd monitor
  % bin/grab-page-simple.sh
  % bin/grab-endpoint-trivial.sh

The first should return a simple HTML page (that doesn't look like an error page).  The second should simply return the string "Woof!".  If it returns an error page (most like a "502 gateway error" string wrapped in an HTML page), you'll need to stop and troubleshoot.  Most likely it will turn out to be a permissions issue somewhere -- but whatever went wrong, most likely the REST services will suffer the same fate.

(5) Stop the service (just so we know how to)::


Start the 'hybrid' gateway 
--------------------------

Exactly analogous as to the trivial service, which should go about like this (up to the process numbers)::

  % cd /opt/uwsgi
  % uwsgi config/hybrid.ini &
  [5] 82994
  [uWSGI] getting INI configuration from config/hybrid.ini

As with the trivial service, we'll need to chown the socket to match the user setting in the nginx.conf (per step 2)::

  % sudo chown nobody /tmp/uwsgi_hybrid.sock

Should now be reachable via nginx; let's try pinging the /lookup URL::

  % cd monitor
  % bin/grab-endpoint-lookup.sh 

Hopefully this won't yield a "502 gateway error".  If things are going well, it should yield a nice little JSOB blob:: 

  {"extras": {"dhcr_active": false, "nychpd_contacts": 5, "taxbill": {"active_date": "2015-06-05", "owner_address": ["DAKOTA INC. (THE)", "1 W. 72ND ST.", "NEW YORK , NY 10023-3486"], "owner_name": "DAKOTA INC. (THE)"}}, "nycgeo": {"bbl": 1011250025, "bin": 1028637, "geo_lat": 40.77640230806594, "geo_lon": -73.97636507868083}}

If it says::

  {"error": "internal error"}

That's actually a good sign, because it means the endpoint is at least reachable.  Most likely it's a configuration or permissions issue at the database level (with one of the config files); but at least the uWSGI gateway is working.

By this point you should have a pretty good indication that both gateways are working and reachable (at least from where you are).  Now you can push the actual frontend client to the HTML root, per the instructions in the ``landlord-lookup-client`` repo.

