import sys, time
import simplejson as json
from lookuptool.geoutils import split_address
# from lookuptool.hybrid.lookup import LookupAgent 
import lookuptool.hybrid.factory

pgconf     = json.loads(open("config/postgres.json","r").read())
nycgeoconf = json.loads(open("config/nycgeo.json","r").read())

if len(sys.argv) > 1:
    rawaddr = sys.argv[1]
else:
    rawaddr = "1 West 72nd St, Manhattan"
    # rawaddr = "529 West 29th St, Manhattan"

address = split_address(rawaddr)
print("address = ",address)

# agent = LookupAgent(pgconf,nycgeoconf)
agent = lookuptool.hybrid.factory.instance(pgconf,nycgeoconf,mock=True)
t0 = time.time()
r = agent.get_combined_summary(address)
delta = 1000 * (time.time() - t0)
print("dt = %.2f millis" % delta)
print(json.dumps(r,indent=4,sort_keys=True))

