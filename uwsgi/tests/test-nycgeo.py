#!/usr/bin/env python
import argparse
import simplejson as json
from nycgeo.client import SimpleGeoClient
from common.logging import log

parser = argparse.ArgumentParser()
parser.add_argument('--addr', help="address to parse")
parser.add_argument('--mock', dest='mock', action='store_true', help="use the mock service")
parser.add_argument('--tiny', dest='tiny', action='store_true', help="fetch a tiny rec")
args = parser.parse_args()

log.info("info!")
log.debug("debug!")

if args.mock:
    configpath = "config/nycgeo-mock.json"
else:
    configpath = "config/nycgeo-live.json"
config = json.loads(open(configpath,"r").read())

if args.addr:
    rawaddr = args.addr
else:
    rawaddr = "529 West 29th St, Manhattan"
print("rawaddr = [%s]" % rawaddr)

agent = SimpleGeoClient(**config)

if args.tiny:
    response,status = agent.fetch_tiny(rawaddr)
else:
    response,status = agent.fetch(rawaddr)

print("status = ", status)
print("response = ",json.dumps(response,indent=True,sort_keys=True))

