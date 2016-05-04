How to import a "pure" database (containing only the hard schema), once it's been exported at the conclusion of the ETL process.

So, one way or another we get it to the gateway host, and do this to import (to database 'nyc2', say)::

  sudo su postgres
  gunzip /var/tmp/pgdump-hard-YYYYMMDD.sql.gz
  /opt/pg9/bin/psql -U writeuser -d nyc2 -f /var/tmp/pgdump-hard-YYYYMMDD.sql

And if this is a freshly created database, you'll also need to create the ``readuser`` role::

  /opt/pg9/bin/psql -U postgres -d nyc2 -f sql/create-roles.sql

Which can be verified by the following sanity check::

  psql -U readuser -d nyc2
  nyc2> select count(*) from hard.property_summary;




