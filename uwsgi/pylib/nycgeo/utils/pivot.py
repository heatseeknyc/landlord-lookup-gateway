#
# DEPRECATED
#
# Utility functions for pivoting (or less elegantly, "scraping") multi-building 
# record results out of the raw dicts structs returned by the NYC Geoclient API.
#
# Basically what happens is that the Geoclient API "vectorizes" its building
# results not by returning a nested dict struct like one would expect, but by 
# returning a giant flat dict per-building fields "indexed" by appending raw 
# integer offsets after the field names (which also happen to start with the
# prefix 'gi').  So have to do some careful parsing for field names of just this 
# type (and not other integer-trailing fields, like "censusTrack2000") and then 
# "pivot" these into a proper nested struct we can actually deal with. 
#
import re
from collections import defaultdict


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



def profile_nycgeo_keys(dictlist):
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
    buildings = [imulti[k] for k in intkeys]
    return {'taxlot':taxlot,'buildings':buildings}


