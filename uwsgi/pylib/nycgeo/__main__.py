import time
import yaml
import argparse
import simplejson as json
from nycgeo.client import SimpleGeoClient
from common.logging import log

LOUD = False
THROW = False

def parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True);
    group.add_argument('--infile', type=str, help="input file")
    group.add_argument('--rawaddr', type=str, help="raw address")
    parser.add_argument('--loud', action="store_true", help="loudness")
    parser.add_argument('--throw', action="store_true", help="throw all exceptions")
    return parser.parse_args()

def do_single(geoclient,rawaddr):
    print(f"rawaddr = '{rawaddr}' ..")
    status,keytup = geoclient.fetch_tiny(rawaddr)
    print(f'status = {status}, keytup = {keytup}')

def main():
    global THROW,LOUD
    args = parse_args()
    LOUD = args.loud
    THROW = args.throw
    log.info('hi')
    log.debug('yow')
    nycgeopath = "config/nycgeo-live.json"
    geoconf  = json.loads(open(nycgeopath,"r").read())
    geoclient = SimpleGeoClient(**geoconf)
    print(f'agent = {geoclient}')
    if args.rawaddr:
        do_single(geoclient,args.rawaddr)
    else:
        raise NotImplementedError("not yet")
    print('done')

if __name__ == '__main__':
    main()


#
# DEPRECATED
#

def __datapath(name):
    if name not in ENDPOINTS:
        raise ValueError("invalid endpoint")
    return "tdata/hybrid/%s.yaml"% name

def __load_data(name):
    infile = datapath(name)
    with open(infile,"rtU") as f:
        return yaml.load(f)

def __runfor(agent,endpoint):
    pairs = load_data(endpoint)
    print("that be %d test cases." % len(pairs))
    delta,status = dotests(endpoint,agent,pairs)
    _status = 'OK' if status else 'BAD'
    print("status = %s in  %.2f ms" % (_status,delta))

def __evaltest(endpoint,agent,spec):
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
        print("EXCEPT %s" % str(e))
        if THROW:
            raise e
        return False




"""
@timedsingle
def dotests(endpoint,agent,pairs):
    for i,r in enumerate(pairs):
        status = evaltest(endpoint,agent,r)
        _status = 'ok' if status else 'FAILED'
        print("test %d => %s" % (i,_status))
    return True
"""

