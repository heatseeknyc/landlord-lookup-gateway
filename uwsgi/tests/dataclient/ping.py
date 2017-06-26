#!/usr/bin/env python
import time, argparse
import simplejson as json
from lookuptool.dataclient import DataClient

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="what to pull")
    parser.add_argument("--key", help="BBL,BIN pair to use as primary key")
    return parser.parse_args()

def derive_keytup(args):
    if args.key:
        print(args)
        print("key = ", args.key)
        _bbl,_bin = map(int,args.key.split(','))
    else:
        _bbl,_bin = 1011250025,1028637
    return  _bbl,_bin

def dispatch(args,pair):
    agent = DataClient(**dataconf)
    t0 = time.time()
    if args.mode == 'summary':
        r = agent.get_summary(_bbl,_bin)
    elif args.mode == 'contacts':
        r = agent.get_contacts(_bbl,_bin)
    else:
        r = agent.get_summary(_bbl,_bin)
    delta = 1000 * (time.time() - t0)
    return r,delta

def main():
    configpath = "config/postgres.json"
    dataconf   = json.loads(open(configpath,"r").read())
    keytup = derive_keytup(args)
    print("bbl,bin = %s" % str(keytup))
    r.delta = dispatch(args,keytup)
    print("dt = %.2f ms" % delta)
    print(json.dumps(r,indent=4,sort_keys=True))

if __name__ == '__main__':
    main()

