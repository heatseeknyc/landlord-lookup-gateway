import time
import yaml
import argparse
import simplejson as json
import gateway.hybrid
from tests.util import compare
from tests.hybrid.util import initconf
from tests.decorators import timedsingle

ENDPOINTS = ('lookup','buildings')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock', dest='mock', action='store_true', help="use the mock service")
    parser.add_argument('--barf', dest='barf', action='store_true', help="barf up config files after reading")
    parser.add_argument('endpoint', nargs='?', default='all')
    return parser.parse_args()

def datapath(name):
    if name not in ENDPOINTS:
        raise ValueError("invalid endpoint")
    return "tdata/hybrid/%s.yaml"% name

def load_data(name):
    infile = datapath(name)
    with open(infile,"rtU") as f:
        return yaml.load(f)

def runfor(agent,endpoint):
    pairs = load_data(endpoint)
    print("that be %d test cases." % len(pairs))
    delta,status = dotests(agent,pairs)
    _status = 'OK' if status else 'BAD'
    print("status = %s in  %.2f ms" % (_status,delta))

def main():
    args = parse_args()
    dataconf,geoconf = initconf(args)
    agent = gateway.hybrid.instance(dataconf,geoconf)
    print("tag = %s" % args.endpoint)
    runfor(agent,args.endpoint)
    print("done.")

def evaltest(agent,spec):
    rawaddr  = spec['query']
    expected = spec['result']
    print("rawaddr = '%s'" % rawaddr)
    print("expected = %s" % expected)
    response = agent.dispatch('lookup',rawaddr)
    print("response = %s" % response)
    status = compare(response,expected)
    print("status = %s" % status)

@timedsingle
def dotests(agent,pairs):
    for r in pairs:
        evaltest(agent,r)
    return True


if __name__ == '__main__':
    main()

