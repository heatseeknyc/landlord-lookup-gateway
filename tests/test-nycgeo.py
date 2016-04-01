import sys
import simplejson as json
from geomisc.utils import split_address
from nycgeo.agent import Agent

configpath = "config/nycgeo.json"
pgconf = json.loads(open(configpath,"r").read())

if len(sys.argv) > 1:
    rawaddr = sys.argv[1]
else:
    rawaddr = "529 West 29th St, Manhattan"

address = split_address(rawaddr)
print("address = ",address)

agent = Agent(**pgconf)
r,dt= agent.fetch_address(**address)
print("dt = %.2f millis" % dt)
print(json.dumps(r,indent=True))

