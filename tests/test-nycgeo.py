#!/usr/bin/env python
import sys, argparse
import simplejson as json
from nycgeo.client.simple import SimpleGeoClient


parser = argparse.ArgumentParser()
parser.add_argument("--addr", help="address to parse")
parser.add_argument("--norm", help="fetch a normalized (pivoted) rec", type=int)
parser.add_argument("--tiny", help="fetch a tiny rec", type=int)
parser.add_argument("--mock", help="use the mock service", type=int)
args = parser.parse_args()
print(args)

if args.mock:
    configpath = "config/mockgeo-client.json"
else:
    configpath = "config/nycgeo.json"
config = json.loads(open(configpath,"r").read())
print(config)

if args.addr: 
    rawaddr = args.addr 
else:
    rawaddr = "529 West 29th St, Manhattan"
print("rawaddr = [%s]" % rawaddr)

agent = SimpleGeoClient(**config)

if args.tiny:
    inforec,status = agent.fetch_tiny(rawaddr)
elif args.norm:
    inforec,status = agent.fetch_norm(rawaddr)
else:
    inforec,status = agent.fetch(rawaddr)

print("status = ", status)
print("inforec = ", json.dumps(inforec,indent=True,sort_keys=True))

