Our current smoktest environment, as such.

These aren't fully automated, but the scripts are intuitive enough, and (once the test daemons are running) it should take just a few manual invocations at the command line to sanity-check the python modules (and just as crucially, your local environment variable set up).

For detailed steps of how to do this during deployment, see the note ``documentation\HOWTO-start-services.rst``.  However, provided the test daemons are running, the scripts can be run from the repo location as well.  The main idea is that you run the scripts from the directory above this one, taking turns with certain flags::

   python3 tests/test-nycgeo.py --mock
   python3 tests/test-hybrid.py --mock
   python3 tests/test-nycgeo.py
   python3 tests/test-hybrid.py

Are the most important ones (and a successful run should inicated that services are basically working).  

The other scripts in this directory provide similar sanity checks, at a somewhat lower level of granularity.

About the --mock flag
---------------------

The main thing to understand is that the services have been built such that the both the inner workings of the gateway -- as well as connectivity to the frontend client -- can, with a few configuration settings, be enabled to run against a completely local, "mock" version of the NYCGeoclient service (which responds in a sway similar to the live NYCGeoclient API, however with limited fields and for just a handful of lookup addresses -- which also need to be exactly specified). 

The mock service itself lives over in the ``daemons`` dir::

  daemons/mockgeo.py

And it pulls its test data from this file::

  tests/data/mockdata.json

And the ``--mock`` flag is used by both daemons and test scripts to test against the mock service rather than the live NYCGeoclient API. 


