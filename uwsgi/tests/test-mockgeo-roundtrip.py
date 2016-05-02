#!/usr/bin/env python
import simplejson as json
import requests
from nycgeo.client import SimpleGeoClient
from nycgeo.utils.address import split_address

clientcfg = json.loads(open("config/nycgeo-mock.json","r").read())
mockdata  = json.loads(open("tests/data/mockdata.json","r").read())
mockaddr  = [r['address'] for r in mockdata]

print(clientcfg)
client = SimpleGeoClient(**clientcfg) 


for r in mockdata:
    address  = r['address']
    expected = r['nycgeo']
    print("address = %s" % address)
    response,status = client.fetch_tiny(address)
    print("status = %s" % status)
    print("response = %s" % response)
    print("expected = %s" % expected)
    # response = agent.lookup(param)
  
