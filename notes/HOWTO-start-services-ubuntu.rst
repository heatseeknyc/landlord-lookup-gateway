Instructions for starting uWSGI/nginx services under Ubuntu.  Probably shouldn't have to change or tweak anything in here. 


uWSGI
-----

(1) init env?

(2) Once the files have been pushed, setup is analogous to the Ubuntu case:

  % cd /opt/uwsgi
  % source bin/init-env-ubunturc
  % which uwsgi
  /path/to/uwsgi
  % uwsgi --python-version
  3.4.3

The last step is crucial because it makes sure uWSGI is set up to find Python 3, not Python 2.

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

(2) Start the service, and make sure there are no complaints: 

  % sudo nginx -p /opt/nginx 

(3) Try a few test URLs:

  % bin/test-page-simple.sh
  % bin/test-endpoint-trivial.sh

The first should return a simple HTML page (that doesn't look like an error page).  The second should simply return the string "Woof!".  If it returns an error page (most like a "502 gateway error" string wrapped in an HTML page), you'll need to stop and troubleshoot.  Most likely it will turn out to be a permissions issue somewhere -- but whatever went wrong, most likely the REST services will suffer the same fate.

(4) Note that if you need to stop the service, here's the preferred way:

  % sudo nginx -p /opt/nginx -s stop



Start the 'hybrid' service
--------------------------

Exactly analogous as to the trivial service:

  % cd /opt/uwsgi
  % uwsgi config/hybrid.ini

Should now be reachable via nginx; let's try pinging the /lookup and /contacts URL:

  bin/grab-endpoint-lookup.sh 
  bin/grab-endpoint-contacts.sh 

Hopefully thse won't yield "502 gateway error" messages.  But if they return with: 

  {"error": "internal error"}

That's actually a good sign, because it means the endpoint is at least reachable.

But if successful, the 'lookup' pull should yield a response like this:

  {"extras": {"dhcr_active": false, "nychpd_contacts": 5, "taxbill": {"active_date": "2015-06-05", "owner_address": ["DAKOTA INC. (THE)", "1 W. 72ND ST.", "NEW YORK , NY 10023-3486"], "owner_name": "DAKOTA INC. (THE)"}}, "nycgeo": {"bbl": 1011250025, "bin": 1028637, "geo_lat": 40.77640230806594, "geo_lon": -73.97636507868083}}

And the 'contacts' pull should yield a meaningful JSON blurb which we won't paste here (just make sure it doesn't look like an error message).




