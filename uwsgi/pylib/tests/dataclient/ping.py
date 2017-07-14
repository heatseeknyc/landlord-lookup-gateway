import time, argparse
import simplejson as json
from gateway.dataclient import DataClient

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="what to pull", default="taxlot")
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

def dispatch(agent,pair,args):
    print("pair = %s" % str(pair))
    _bbl,_bin = pair
    t0 = time.time()
    if args.mode == 'taxlot':
        r = agent.get_taxlot(_bbl)
    elif args.mode == 'contacts':
        r = agent.get_contacts(_bbl,_bin)
    else:
        raise ValueError("invalid usage - unknown mode")
    delta = 1000 * (time.time() - t0)
    return r,delta

def init_agent(configpath):
    dataconf   = json.loads(open(configpath,"r").read())
    return DataClient(**dataconf)

def main():
    args = parse_args()
    keytup = derive_keytup(args)
    agent = init_agent("config/postgres.json")
    print("bbl,bin = %s" % str(keytup))
    r,delta = dispatch(agent,keytup,args)
    print("dt = %.2f ms" % delta)
    print(json.dumps(r,indent=4,sort_keys=True))

if __name__ == '__main__':
    main()

