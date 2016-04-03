import sys
import simplejson as json
from lookuptool.geoutils import split_address
# from nycgeo.agent import SimpleGeoClient as GeoClient
from nycgeo.mockagent import MockGeoClient as GeoClient

configpath = "config/nycgeo.json"
nycgeoconf = json.loads(open(configpath,"r").read())
fields = ('bbl','latitude','longitude')

if len(sys.argv) > 1:
    rawaddr = sys.argv[1]
else:
    rawaddr = "529 West 29th St, Manhattan"

query = split_address(rawaddr)
print("query = ",query)
if query is None:
    raise ValueError("invalid address (cannot parse)")

agent = GeoClient(**nycgeoconf)
inforec,status = agent.fetch(query,fields)
print("status = ", status)
print("inforec = ", json.dumps(inforec,indent=True))

