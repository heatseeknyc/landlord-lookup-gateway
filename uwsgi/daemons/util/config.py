import os
from gateway.util.misc import slurp_json
from common.logging import log

# A simple idiom to make our file loading a bit more tidy
def load_file(confdir,filename):
    if not os.path.exists(confdir):
        raise RuntimeError("can't find config dir '%s'" % confdir)
    path = "%s/%s" % (confdir,filename)
    return slurp_json(path)

def load_hybrid_conf(confdir,args):
    """Loads the requisite config files for the hybrid service (subject to
    arg switches), and returns them as a tuple of (dataconf,geoconf)."""
    metaconf = load_file(confdir,'hybrid-settings.json')
    dataconf = load_file(confdir,'postgres.json')
    if args.mock:
        usemock = True
    elif args.nomock:
        usemock = False
    else:
        usemock = metaconf['mock']
    log.info("mock = %s, port = %d" % (usemock,args.port))
    suffix = 'mock' if usemock else 'live';
    geofile = "nycgeo-%s.json" % suffix
    geoconf = load_file(confdir,geofile)
    log.info("siteurl = '%s'" % geoconf.get('siteurl'))
    return dataconf,geoconf

