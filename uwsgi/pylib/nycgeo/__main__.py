import time
import yaml
import argparse
import simplejson as json
import ioany
from itertools import islice
from collections import OrderedDict
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
    parser.add_argument('--limit', type=int, required=False, help="limit")
    return parser.parse_args()

def do_single(geoclient,rawaddr):
    log.debug(f"rawaddr = '{rawaddr}' ..")
    status, keytup = geoclient.fetch_tiny(rawaddr)
    log.debug(f'status = {status}, keytup = {keytup}')
    return status, keytup

def do_multi(geoclient,records,loud=False):
    log.info("let's do this ...")
    stream = procmulti(geoclient,records,loud)
    ioany.save_recs("this.csv",stream)

def procmulti(geoclient,records,loud=False):
    for i,r in enumerate(records):
        log.info(f'proc {i} ..')
        d = process(geoclient,r,i)
        if loud:
            print(d)
        yield d

def process(geoclient,r,i):
    rawaddr = makeaddr(r)
    log.info(f'{i}: {rawaddr} ..')
    d = OrderedDict(r)
    try:
        status, keytup = do_single(geoclient,rawaddr)
        d['code'] = status.get('code')
        d['bbl'] = keytup['bbl']
        d['bin'] = keytup['bin']
        d['error'] = status.get('error')
        d['message'] = keytup.get('message')
    except Exception as e:
        errmsg = str(e)
        log.info(f'{i}: ERROR {errmsg}')
        log.error(e)
        d['error'] = errmsg
    return d

def makeaddr(r):
    return "{address}, {borough}".format(**r)

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
        infile = args.infile
        print(f'slurp from {infile} ..')
        inrecs = ioany.read_recs(infile)
        inrecs = islice(inrecs,args.limit)
        do_multi(geoclient,inrecs)

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

