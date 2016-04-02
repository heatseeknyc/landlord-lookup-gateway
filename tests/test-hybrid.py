import sys
import simplejson as json
from lookuptool.geoutils import split_address
from lookuptool.agent import HybridAgent 

pgconf     = json.loads(open("config/postgres.json","r").read())
nycgeoconf = json.loads(open("config/nycgeo.json","r").read())

if len(sys.argv) > 1:
    rawaddr = sys.argv[1]
else:
    rawaddr = "529 West 29th St, Manhattan"

address = split_address(rawaddr)
print("address = ",address)

agent = HybridAgent(pgconf,nycgeoconf)
r,dt = agent.get_combined_summary(address)
print("dt = %.2f millis" % dt)
print(json.dumps(r,indent=True))

