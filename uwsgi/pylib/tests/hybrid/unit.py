import time
import yaml
import argparse
import simplejson as json
import lookuptool.hybrid
from tests.util import compare

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock', dest='mock', action='store_true', help="use the mock service")
    parser.add_argument('--barf', dest='barf', action='store_true', help="barf up config files after reading")
    return parser.parse_args()

def init_conf(args):
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

def main():
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

def evaltest(agent,spec):
    rawaddr  = spec['query']['rawaddr']
    expected = spec['result']
    print("rawaddr = '%s'" % rawaddr)
    print("expected = %s" % expected)
    response = agent.get_lookup(rawaddr)
    print("response = %s" % response)
    status = compare(response,expected)
    print("status = %s" % status)

def dotests(agent,pairs):
    for r in pairs:
        evaltest(agent,r)

if __name__ == '__main__':
    main()



