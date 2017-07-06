import time, argparse
import simplejson as json
import lookuptool.hybrid
from tests.hybrid.util import init_conf

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', help="address to search", default="1 West 72nd St, Manhattan")
    parser.add_argument('--mock', dest='mock', action='store_true', help="use the mock service")
    parser.add_argument('--barf', dest='barf', action='store_true', help="barf up config files after reading")
    return parser.parse_args()

"""
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
"""

def main():
    args = parse_args()
    rawaddr = args.addr
    print("rawaddr = [%s]" % rawaddr)
    dataconf,geoconf = init_conf(args)
    agent = lookuptool.hybrid.instance(dataconf,geoconf)
    t0 = time.time()
    r = agent.get_lookup(rawaddr)
    delta = 1000 * (time.time() - t0)
    print("dt = %.2f millis" % delta)
    print(json.dumps(r,indent=4,sort_keys=True))

    print("the lovely new main")

if __name__ == '__main__':
    main()

