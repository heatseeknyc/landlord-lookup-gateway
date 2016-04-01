import os, logging

logging.basicConfig(
  filename = "log/nycgeo-error-%d.log" % os.getpid(),
  format   = "%(levelname)s %(funcName)s %(message)s",
  level    = logging.INFO
)
log = logging.getLogger('app')

