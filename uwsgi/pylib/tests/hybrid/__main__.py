import time
import yaml
import argparse
import simplejson as json
import gateway.hybrid
from tests.util import compare
from tests.hybrid.util import initconf
from tests.decorators import timedsingle

LOUD = False
ENDPOINTS = ('lookup','buildings')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--loud', dest='loud', action='store_true', required=False)
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
    delta,status = dotests(endpoint,agent,pairs)
    _status = 'OK' if status else 'BAD'
    print("status = %s in  %.2f ms" % (_status,delta))

def main():
    global LOUD
    args = parse_args()
    LOUD = args.loud
    dataconf,geoconf = initconf(args)
    agent = gateway.hybrid.instance(dataconf,geoconf)
    print("tag = %s" % args.endpoint)
    runfor(agent,args.endpoint)
    print("done.")

def evaltest(endpoint,agent,spec):
    query = spec['query']
    expected = spec['result']
    if LOUD:
        print("query    = '%s'" % query)
        print("expected = %s" % expected)
    try:
        response = agent.dispatch(endpoint,query)
        if LOUD:
            print("response = %s" % response)
        return compare(response,expected)
    except Exception as e:
        print("FAILED = %s" % str(e))
        # raise e
        return False


@timedsingle
def dotests(endpoint,agent,pairs):
    for i,r in enumerate(pairs):
        status = evaltest(endpoint,agent,r)
        _status = 'ok' if status else 'FAILED'
        print("test %d => %s" % (i,_status))
    return True


if __name__ == '__main__':
    main()

