#!/usr/bin/env python
import time, argparse
import simplejson as json
import lookuptool.hybrid

parser = argparse.ArgumentParser()
parser.add_argument('--addr', help="addres to search")
parser.add_argument('--mock', dest='mock', action='store_true', help="use the mock service")
parser.add_argument('--barf', dest='barf', action='store_true', help="barf up config files after reading")
args = parser.parse_args()

if args.mock:
    nycgeopath = "config/nycgeo-mock.json"
else:
    nycgeopath = "config/nycgeo-live.json"

dataconf = json.loads(open("config/postgres.json","r").read())
geoconf  = json.loads(open(nycgeopath,"r").read())
if args.barf:
    print("dataconf =",dataconf)
    print("geoconf = ",geoconf)

if args.addr:
    rawaddr = args.addr
else:
    rawaddr = "1 West 72nd St, Manhattan"
    # rawaddr = "529 West 29th St, Manhattan"


print("rawaddr = [%s]" % rawaddr)
agent = lookuptool.hybrid.instance(dataconf,geoconf)
t0 = time.time()
r = agent.get_lookup(rawaddr)
delta = 1000 * (time.time() - t0)
print("dt = %.2f millis" % delta)
print(json.dumps(r,indent=4,sort_keys=True))

