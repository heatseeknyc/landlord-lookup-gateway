#!/usr/bin/env python
#
# DEPRECATED - this test isn't needed for normal smoketesting.
#
# Tests against a few record pivoting functions, not currently used.
#
import sys
import simplejson as json
from nycgeo.pivot import pivot_nycgeo, pivot_nycgeo_partial, profile_nycgeo_keys, is_gi_key


filename = sys.argv[1]
d = json.loads(open(filename,"r").read())
print("dict with %d keys." % len(d))

rawkeys = list(d.keys())
print("got %d raw keys." % len(rawkeys))
gikeys = list(filter(is_gi_key,d.keys()))
print("got %d filtered keys." % len(gikeys))
core,multi = pivot_nycgeo_partial(d)

print("core with %d keys." % len(core))
print("multi with %d keys." % len(multi))
core_keys = sorted(list(core.keys()))
print("cor keys = ",json.dumps(core_keys,sort_keys=True,indent=True))
print("multi keys = %s" % sorted(list(multi.keys())))

profile = profile_nycgeo_keys(list(multi.values()))
print("profile = ",json.dumps(profile,sort_keys=True,indent=True))

print("now...")
r = pivot_nycgeo(d)
print(json.dumps(r,sort_keys=True,indent=True))


