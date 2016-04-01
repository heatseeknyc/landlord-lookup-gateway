import sys
import simplejson as json
from lookuptool.agent import PartialAgent

configpath = "config/postgres.json"
pgconf = json.loads(open(configpath,"r").read())

if len(sys.argv) > 1:
    bbl = int(sys.argv[1])
else:
    bbl = 1007017501

print("bbl = ",bbl)

agent = PartialAgent(**pgconf)
# r,dt = agent.get_lookup(bbl)
# print("dt = %.2f millis" % dt)
r = agent.get_lookup(bbl)
print(json.dumps(r,indent=True))

