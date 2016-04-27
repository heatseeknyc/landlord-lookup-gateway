import os, sys, logging

def app_name():
    script = os.path.basename(sys.argv[0])
    return script.split('.')[0]

logging.basicConfig(
  filename = "log/%s-%d.log" % (app_name(),os.getpid()),
  format   = "%(levelname)s - %(asctime)s :: %(funcName)s :: %(message)s",
  level    = logging.INFO
)
log = logging.getLogger()

