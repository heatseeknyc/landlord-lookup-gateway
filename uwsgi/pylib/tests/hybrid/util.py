import time
import yaml
import simplejson as json
import lookuptool.hybrid
from tests.util import compare

def initconf(args):
    if args.mock:
        nycgeopath = "config/nycgeo-mock.json"
    else:
        nycgeopath = "config/nycgeo-live.json"

    dataconf = json.loads(open("config/postgres.json","r").read())
    geoconf  = json.loads(open(nycgeopath,"r").read())
    if args.barf:
        print("dataconf =",dataconf)
        print("geoconf = ",geoconf)
    return dataconf,geoconf

def __main():
    args = parse_args()
    dataconf,geoconf = init_conf(args)
    agent = lookuptool.hybrid.instance(dataconf,geoconf)
    with open("tdata/hybrid.yaml","rtU") as f:
        pairs = yaml.load(f)
    print("that be %d test cases." % len(pairs))
    t0 = time.time()
    dotests(agent,pairs)
    delta = 1000 * (time.time() - t0)
    print("dt = %.2f millis" % delta)
    print("done.")

def __evaltest(agent,spec):
    rawaddr  = spec['query']['rawaddr']
    expected = spec['result']
    print("rawaddr = '%s'" % rawaddr)
    print("expected = %s" % expected)
    response = agent.get_lookup(rawaddr)
    print("response = %s" % response)
    status = compare(response,expected)
    print("status = %s" % status)

def __dotests(agent,pairs):
    for r in pairs:
        __evaltest(agent,r)

