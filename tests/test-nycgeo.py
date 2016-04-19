import sys, argparse
import simplejson as json
# from lookuptool.geoutils import split_address
import nycgeo.factory


parser = argparse.ArgumentParser()
parser.add_argument("--mock", help="use a mock agent", type=int)
parser.add_argument("--tiny", help="get a 'tiny' rec based on restricted fields", type=int)
parser.add_argument("--addr", help="address to parse")
args = parser.parse_args()
print(args)

configpath = "config/nycgeo.json"
nycgeoconf = json.loads(open(configpath,"r").read())

if args.addr: 
    rawaddr = args.addr 
else:
    rawaddr = "529 West 29th St, Manhattan"

print("rawaddr = [%s]" % rawaddr)

agent = nycgeo.factory.instance(config=nycgeoconf,mock=bool(args.mock))
print("agent = ",agent)

fields = ('bbl','bin','geo_lat','geo_lon')
if args.tiny:
    inforec,status = agent.fetch(rawaddr,fields)
else:
    inforec,status = agent.fetch(rawaddr)
print("status = ", status)
print("inforec = ", json.dumps(inforec,indent=True,sort_keys=True))

