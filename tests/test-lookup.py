#!/usr/bin/env python
import sys, time, argparse
import simplejson as json
from nycgeo.utils.address import split_address
from lookuptool import get_lookup_agent

parser = argparse.ArgumentParser()
parser.add_argument("--mock", help="route geoclient calls to mock service", type=int)
parser.add_argument("--addr", help="addres to search")
args = parser.parse_args()

if args.mock:
    nycgeopath = "config/mockgeo-client.json"
else:
    nycgeopath = "config/nycgeo.json"

dataconf = json.loads(open("config/postgres.json","r").read())
geoconf  = json.loads(open(nycgeopath,"r").read())
print(dataconf)
print(geoconf)

if args.addr: 
    rawaddr = args.addr 
else:
    rawaddr = "529 West 29th St, Manhattan"
print("rawaddr = [%s]" % rawaddr)


if len(sys.argv) > 1:
    rawaddr = sys.argv[1]
else:
    rawaddr = "1 West 72nd St, Manhattan"

address = split_address(rawaddr)
print("address = ",address)

agent = get_lookup_agent(dataconf=dataconf,geoconf=geoconf)
print("agent = ",agent)
sys.exit(1)
t0 = time.time()
r = agent.get_combined_summary(address)
delta = 1000 * (time.time() - t0)
print("dt = %.2f millis" % delta)
print(json.dumps(r,indent=4,sort_keys=True))

