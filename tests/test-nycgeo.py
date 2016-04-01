import sys
import simplejson as json
from nycgeo.agent import Agent

configpath = "config/nycgeo.json"
pgconf = json.loads(open(configpath,"r").read())


agent = Agent(**pgconf)
r,dt= agent.fetch_address(
        house_number="529",
        street_name="West+29th+St",
        boro_name="Manhattan"
    )
print("dt = %.2f millis" % dt)
print(json.dumps(r,indent=True))


