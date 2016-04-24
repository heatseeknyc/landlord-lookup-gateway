#!/usr/bin/env python
import simplejson as json
from nycgeo.server.agent import GeoServerMockAgent
from nycgeo.utils.address import split_address, address2param

datapath = "tests/data/mockdata.json"
mockdata = json.loads(open(datapath,"r").read())
mockaddr = [r['address'] for r in mockdata]

agent = GeoServerMockAgent(mockdata)
# for k in agent.data:
#    print("k = %s, v = %s" % (k,agent.data.get(k)))

for address in mockaddr:
    # print("address = %s" % address)
    param = split_address(address)
    # print("param = %s" % str(param))
    response = agent.lookup(param)
    print("%s: %s" % (address,response))

