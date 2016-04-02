import sys
import simplejson as json
from lookuptool.geoutils import split_address
from nycgeo.agent import SimpleGeoclient 

configpath = "config/nycgeo.json"
nycgeoconf = json.loads(open(configpath,"r").read())

if len(sys.argv) > 1:
    rawaddr = sys.argv[1]
else:
    rawaddr = "529 West 29th St, Manhattan"

address = split_address(rawaddr)
print("address = ",address)

agent = SimpleGeoclient(**nycgeoconf)
r,dt= agent.fetch_address(**address)
print("dt = %.2f millis" % dt)
print(json.dumps(r,indent=True))

