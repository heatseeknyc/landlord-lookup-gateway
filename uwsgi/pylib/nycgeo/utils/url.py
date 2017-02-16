import re
from collections import defaultdict

"""
A simple query string splitter, for use in testing environments.
Takes a query string of the form:

   'borough=3&street=Bushwick+Ave&houseNumber=590'

and returns the appropriate dict.
"""

def split_kv(term):
    kv = term.split('=')
    if len(kv) == 1:
        return (kv[0],'')
    if len(kv) == 2:
        return tuple(kv)
    raise ValueError("bad term ['%s'] in query string" % term)

def _decode(s):
    return s.replace('+',' ')

def decode_pairs(pairs):
    return [ (_decode(k),_decode(v)) for k,v in pairs ]

def split_query_classic(s):
    r = defaultdict(list)
    terms = s.split('&')
    pairs = [split_kv(t) for t in terms]
    pairs = decode_pairs(pairs)
    for k,v in pairs:
        r[k].append(v)
    return dict(r)

def split_query(s):
    d = split_query_classic(s)
    return {k:d[k][0] for k in d}



# deprecated
pat = re.compile('^(.*?)?(.*)$')
def split_baseurl(baseurl):
    m = pat.match(baseurl)
    if m:
        base = m.group(1)
        params = split_query(m.group(2))
        return base,params
    else:
        return baseurl,None


