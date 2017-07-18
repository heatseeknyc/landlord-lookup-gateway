"""
An unimaginatively named "data client" agent that provides simple accessors
for the record pulls we're likely to need in our UI (along with a few other
secret ones for diagnosis).
"""
from .base import AgentBase
from common.logging import log
from copy import deepcopy
import simplejson as json
import datetime

class DataClient(AgentBase):

    def get_taxlot(self,bbl):
        log.debug("bbl = %s")
        if bbl is None:
            return None
        query = "select * from deco.taxlot where bbl = %s"
        r = self.fetchone(query,bbl)
        log.debug("r = %s" % r)
        return stagger_taxlot(r)

    # Note that there's no special treatment for invalid BBLs/BINs at this stage:
    # in theory they should already excluded from the database, so queries on them
    # simply return empty results.  We do exclude null BBLs, however.
    def get_buildings(self,_bbl,_bin=None):
        log.debug("bbl = %s, bin = %s" % (_bbl,_bin))
        if _bbl is None:
            return []
        if _bin is None:
            query = "select * from hard.building where bbl = %s and in_pluto order by bin, doitt_id"
            args = (_bbl,)
        else:
            query = "select * from hard.building where bbl = %s and bin = %s and in_pluto order by doitt_id"
            args = (_bbl,_bin)
        r = self.fetch_recs(query,*args)
        log.debug("fetched type(r) = %s" % type(r))
        log.debug("fetched r = %s" % r)
        if r:
            [inflate_shape(_) for _ in r]
        return r

    def get_contacts(self,_bbl,_bin):
        '''HPD contacts per BBL'''
        query = \
            "select contact_id, registration_id, contact_type, description, corpname, contact_name, business_address " + \
            "from hard.contact_info where bbl = %s and bin = %s order by registration_id, contact_rank;"
        return self.fetch_recs(query,_bbl,_bin)


def _trunc(k,n):
    """Simply truncates first :n characters fron the (presumably) well-formed dict :key
    if possible to do so; otherwise, throws an exception relevant to the particular
    function we're calling it from."""
    if len(k) > n:
        return k[n:]
    else:
        raise ValueError("invalid key '%s' relative to prefix '%s'" (tag,prefix))

def clear_none(r,members=None):
    """Given a dict, delete all keys which reference None values"""
    if members is None:
        members = sorted(r.keys())
    for k in members:
        if r[k] is None:
            del r[k]

def extract_prefixed(r,prefix,collapse=True,prune=False,clear=False):
    prefix_ = prefix+'_'
    x,n = {},len(prefix_)
    tags = sorted(k for k in r.keys() if k.startswith(prefix_))
    for k in tags:
        j = _trunc(k,n)
        x[j] = deepcopy(r[k])
        if prune:
            del r[k]
    if clear:
        clear_none(x)
    if collapse and len(x) == 0 or all(v is None for v in x.values()):
        return None
    return x

def fixdates(r):
    for k,v in r.items():
        if isinstance(v,datetime.date):
            r[k] = str(v)

def inflate_shape(r):
    if r:
        applymems(r,jsonify,['parts','points'])

def _pluto_bldg_count_label(n):
    if n is None or n < 1: 
        return "A vacant lot"
    else:
        s = 's' if n > 1 else ''
        return "A lot with %d building%s" % (n,s)

def augment_pluto(p):
    """Augment pluto struct with nice descriptive fields (in-place)."""
    if not p:
        return
    p['bldg_count_label'] = _pluto_bldg_count_label(p['bldg_count'])

#
# Because nested is better than flat.
#
def stagger_taxlot(r):
    """Invasively 'staggers' a database response to a taxlot query. returning
    a new bilevel dict and mangling the old one beyond recognition."""
    if r is None:
        return None
    rr = {}
    # There's a bit of repetition here, but it make it clear which members 
    # we're extracting.  Also, if we need to tweak the extraction parameters
    # at some point, we have the option of doing that.
    rr['hpd']   = extract_prefixed(r,'hpd',prune=True)
    rr['pluto'] = extract_prefixed(r,'pluto',prune=True)
    rr['acris'] = extract_prefixed(r,'acris',prune=True,clear=True)
    rr['stable'] = extract_prefixed(r,'stable',prune=True,clear=True)
    rr['condo'] = extract_prefixed(r,'condo',prune=True,clear=True)
    rr['meta'] = deepcopy(r)
    if rr['acris']:
        adjust_acris(rr['acris'])
    if rr['pluto']:
        inflate_shape(rr['pluto'])
        augment_pluto(rr['pluto'])
    # adjust_condo(rr['condo'])
    return rr

def adjust_acris(acris):
    fixdates(acris)
    amount = acris.get('amount')
    if amount is not None:
        acris['amount'] = round(amount)

def pluck(d,k):
    if k not in d:
        raise KeyError("invalid usage - can't pluck non-existent key '%s'" % k)
    v = d[k]
    del d[k]
    return v

def applymems(r,callf,keys):
    for k in keys:
        if k in r:
            r[k] = callf(r[k])

def jsonify(x):
    return None if x is None else json.loads(x)



#
# Deprecated Section
#

"""
Splits the taxbill owner addresss on the embedded '\\n' string
(literally '\'+'\'+'n') from an incoming string, which we take to
be an encoding of "\n"; e.g:

  'DAKOTA INC. (THE)\\n1 W. 72ND ST.\\nNEW YORK , NY 10023-3486'

then strips whitespace from the resulting terms, and returns a nice
list struct.
"""
def expand_address(s):
    if s is None:
        return None
    terms = s.split('\\n')
    return [t.strip() for t in terms]

_shape_fields = ('lat_ctr','lon_ctr','radius','points','parts')
def extract_shape(r):
    return extract_fields(r,_shape_fields)

def extract_fields(d,keys):
    """Invasively extracts a sequence of key-val from a given dict :d,
    returning these as a new dict."""
    x = {}
    for k in keys:
        if k in d:
            x[k] = d[k]
            del d[k]
        else:
            x[k] = None
    return x

def make_summary_query(_bbl,_bin):
    """
    Magically creates both SQL query and args tuple based on BIN status (null or non-null).

    As descriped in the comments to the 'hard.property_summary' table, which the 'deco'
    view pulls from, the intended select semantics differ depending on whether we're
    searching on a (BBL,BIN) pair or on a single BBL (hence the 'limit 1' business).
    So either way, we're guaranteed to fetch at most a single row.
    """
    if _bbl is None:
        raise ValueError("invalid usage -- can't get summary data without a BBL")
    basequery = "select * from deco.property_summary where bbl = %s"
    if _bin is None:
        query = basequery + " limit 1"
        args = (_bbl,)
    else:
        query = basequery + " and bin = %s"
        args = (_bbl,_bin)
    return query,args

"""
def trim_null(r,members):
    for k in members:
        if k in r and r[k] is None:
            del r[k]
"""

