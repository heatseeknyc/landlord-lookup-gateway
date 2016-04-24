#!/usr/bin/env python
import simplejson as json
from nycgeo.server.agent import GeoServerMockAgent
from nycgeo.utils.address import split_address

datapath = "tests/data/mockdata.json"
mockdata = json.loads(open(datapath,"r").read())
mockaddr = [r['address'] for r in mockdata]

agent = GeoServerMockAgent(mockdata)
# for k in agent.data:
#    print("k = %s, v = %s" % (k,agent.data.get(k)))

for rawaddr in mockaddr:
    param = split_address(rawaddr)
    response = agent.lookup(param)
    print("'%s': %s" % (rawaddr,response))

