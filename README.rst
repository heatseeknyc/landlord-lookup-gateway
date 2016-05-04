A simple PostgreSQL backend + REST gateway for the Landlord Lookup portal. 

The code is organized into two major branches, ``nginx`` and ``uwsgi``, each of which gets pushed more or less as-is into the default locations::

  /opt/nginx
  /opt/uwsgi

Corresponding to the local configurations for those two services, respectively.  The REST API itself (and supporting Python modules) are found under the ``uwsgi`` tree.  The key component is the flask service ``lookup.py``; which, along with a few mock services, are located under the ``daemons`` subdir; these in turn make reference to supporting code under the ``pylib`` dir.


REST protocol
-------------

Is described here::
 
  documentation/ABOUT-rest-protocol.rst

Deployment
----------

See the notes::

  documentation\HOWTO-import-database.rst
  documentation\HOWTO-start-services.rst

Testing
-------

Some lightweight ("smoke-") tests are available under the ``uwsgi/tests`` dir.  See the README there for details.
