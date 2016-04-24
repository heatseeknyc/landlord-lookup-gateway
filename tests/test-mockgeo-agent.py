#!/usr/bin/env python
import simplejson as json
from nycgeo.endpoint.agent import MockAgent
from nycgeo.utils.address import split_address

datapath = "tests/data/mockdata.json"
mockdata = json.loads(open(datapath,"r").read())
mockaddr = [r['address'] for r in mockdata]

agent = MockAgent(mockdata)

for address in mockaddr:
    param = split_address(address)
    response = agent.lookup(param)
    print("%s: %s" % (param,response))

