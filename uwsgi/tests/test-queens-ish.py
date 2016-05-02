#!/usr/bin/env python
from lookuptool.utils.address import fix_queens_name
import lookuptool.hybrid
import simplejson as json

#
# A simple unit test (and our only unit test) for "Queensish"
# borough name munging.  See the comments to the 'fix_queens_name'
# callable for details.
#

rawaddr  = '10-87 Jackson Ave, Long Island City'
normaddr = fix_queens_name(rawaddr)
expected = '10-87 Jackson Ave, Queens'

print("raw: %s" % rawaddr)
print("got: %s" % normaddr)
print("exp: %s" % expected)

dataconf = json.loads(open("config/postgres.json","r").read())
geoconf  = json.loads(open("config/nycgeo-mock.json","r").read())
agent = lookuptool.hybrid.instance(dataconf,geoconf)
r = agent.get_lookup(rawaddr)
print(json.dumps(r,indent=4,sort_keys=True))

