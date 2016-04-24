#!/usr/bin/env python
import simplejson as json
import time, requests
from nycgeo.utils.address import split_address

mockdata  = json.loads(open("tests/data/mockdata.json","r").read())
mockaddr  = [r['address'] for r in mockdata]

siteurl = 'http://localhost:5002'

def makebase(address):
    encoded = address.replace(' ','+')
    return '/lookup/'+encoded

def perform_request(address):
    baseurl = makebase(x['address'])
    t0 = time.time()
    r = requests.get(siteurl+baseurl)
    delta = 1000 * (time.time() - t0)
    status = {"code":r.status_code,"delta":delta}
    response = r.json() if r.status_code == 200 else None
    return response,status

for x in mockdata:
    print("expected.address = %s" % x['address'])
    print("expected.nygeo = %s" % x['nycgeo']) 
    print("expected.extras = %s" % x['extras']) 
    response,status = perform_request(x['address'])
    print("status = %s" % status) 
    if status['code'] == 200:
        print("response.nycgeo = %s" % response.get('nycgeo'))
        print("response.extras = %s" % response.get('extras'))


  
