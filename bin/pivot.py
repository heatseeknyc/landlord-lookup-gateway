#!/usr/bin/env python
import sys, re, argparse
import simplejson as json
from collections import defaultdict
from nycgeo.utils.address import split_address


filename = sys.argv[1]
d = json.loads(open(filename,"r").read())
print("dict with %d keys." % len(d))


indexpat = re.compile('^(.*?)(\d+)$')
def splitkey(s):
    m = indexpat.match(s)
    if m:
        return m.group(1),m.group(2)
    else:
        return s,None 

def pivot_generic(d):
    core = {}
    multi = defaultdict(dict)
    for k in sorted(d.keys()):
        base,index = splitkey(k)
        if index is not None:
            multi[index][base] = d[k] 
        else:
            core[k] = d[k]
    return core,multi

# Need to exclude keys like 'censusTract2000' before we attempt 
# to split on index number.
censuspat = re.compile('^census.*?\d{4}$')


def olde_pivot_nycgeo(d):
    core = {}
    multi = defaultdict(dict)
    for k in sorted(d.keys()):
        if censuspat.match(k):
            core[k] = d[k]
            continue
        base,index = splitkey(k)
        if index is not None:
            multi[index][base] = d[k] 
        else:
            core[k] = d[k]
    return core,multi



# XXX optimize
def profile_keys(dictlist):
    count = defaultdict(int) 
    for d in dictlist:
        for k in d:
            count[k] += 1
    return count

gipat = re.compile('^gi.*?\d+$')
def is_gi_key(k):
    return bool(gipat.match(k))

def pivot_nycgeo_partial(d):
    core = {}
    multi = defaultdict(dict)
    for k in d.keys():
        if is_gi_key(k):
            base,index = splitkey(k)
            if index is not None:
                multi[index][base] = d[k] 
            else:
                raise RuntimeError("invalid state")
        else:
            core[k] = d[k]
    return core,multi


def pivot_nycgeo(d):
    taxlot,multi = pivot_nycgeo_partial(d)
    imulti = {int(k):multi[k] for k in multi.keys()}
    intkeys = sorted(list(imulti.keys()))
    # print("btw: ",{k:len(imulti[k]) for k in imulti}) 
    buildings = [imulti[k] for k in intkeys]
    return {'taxlot':taxlot,'buldings':buildings}


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

profile = profile_keys(list(multi.values()))
print("profile = ",json.dumps(profile,sort_keys=True,indent=True))

print("now...")
r = pivot_nycgeo(d)
print(json.dumps(r,sort_keys=True,indent=True))



