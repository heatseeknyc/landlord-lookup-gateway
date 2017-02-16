
This is one of 3 project repos for the HeatSeek Landlord Lookup portal, currently up and running under:

    https://lookup.heatseek.org/

This repo provides the REST gateway -- basically a pair of lightweight Flask services which listen to requests from the client, and access records (read-only) from a PostgreSQL database.   The assumption is that one way or another, you have the database already build -- most likely by importing an image (a SQL dump) created as the end product of the associated data pipeline.  The pipeline itself can be reproduced from the repo:

- https://github.com/heatseeknyc/landlord-lookup-pipeline

And the web client is provide by this repo:

- https://github.com/heatseeknyc/landlord-lookup-client

Structure
---------

The code is organized into two major branches, ``nginx`` and ``uwsgi``, each of which gets pushed more or less as-is into the default locations::

  /opt/nginx
  /opt/uwsgi

Corresponding to the local configurations for those two services, respectively.  The REST API itself (and supporting Python modules) are found under the ``uwsgi`` tree.  The key component is the flask service ``lookup.py``; which, along with a few mock services, are located under the ``daemons`` subdir; these in turn make reference to supporting code under the ``pylib`` dir.


REST protocol
-------------

Is described here::
 
  notes/ABOUT-rest-protocol.rst

Deployment
----------

These writeups need some love, but aren't too far off from reality::

  notes/deploy-and-start-services.rst
  notes/HOWTO-import-database.rst

Testing
-------

Some lightweight ("smoke-") tests are available under the ``uwsgi/tests`` dir.  See the README there for details.
