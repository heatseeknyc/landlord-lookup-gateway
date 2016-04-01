A simple PostgreSQL backend + REST gateway for the Landlord Lookup portal. 

The key component is the flask service `lookup.py`; which, along with a few mock services, are located under the `daemons` subdir; these in turn make reference to supporting code under the `pylib` dir.

And the `export` dir contains minimalist configuration files for `nginx` and `uwsgi`.  We still haven't fully automated (or documented) the process for deploying these on a bare metal host (though notes were taken from the last install we did, and we hope to be able to provide these also, shortly). 

