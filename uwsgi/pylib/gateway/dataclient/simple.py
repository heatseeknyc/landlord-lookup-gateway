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
        """
        The 'taxlot' struct is a catch-all container for "everything we know
        about the taxlot for a given BBL."  The final struct will have variously
        different members, depending on whether we're in Pluto, ACRIS, or both;
        whether we're a condo baselot or unit, etc.

        But it always has a 'meta' member which provides a few high-level flags
        (like 'is_bank', 'is_resi', etc) as well as reflecting the BBL back as well,
        to make response handling a bit easier.
        """
        log.debug("bbl = %s")
        if bbl is None:
            return None
        # A silly switch we sometimes activate to force a high-level
        # exception to be triggered.
        # if bbl % 2:
        #    raise ValueError("odd-numbered BBLs not allowed")
        query = "select * from deco.taxlot where bbl = %s"
        r = self.fetchone(query,bbl)
        log.debug("r = %s" % r)
        return stagger_taxlot(r)

    def get_baselot(self,bbl):
        """
        This method is currently more of a helper accessor for 'get_taxlot',
        as it isn't currently (directly) attached to any endpoint.  It feches
        a minified 'plutoid' struct for the given BBL (assumed to be a 'bank' BBL),
        so that it can be attached a child to the 'condo' struct in the outgoing
        taxlot struct proper.

        Currently it's only intended usage is to be called via from the hybrid
        agent if it detects that the incoming BBL is a bank bbl.
        """
        log.debug("bbl = %s")
        if bbl is None:
            return None
        query = "select * from deco.baselot where bbl = %s"
        r = self.fetchone(query,bbl)
        log.debug("r = %s" % r)
        return adjust_baselot(r)

    # Note that there's no special treatment for invalid BBLs/BINs at this stage:

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
    adjust_acris(rr['acris'])
    adjust_pluto(rr['pluto'])
    adjust_stable(rr['stable'])
    # Clear all member structs, if void.   
    # But the 'meta' struct should always be present.
    clear_none(rr);
    rr['meta'] = deepcopy(r)
    adjust_meta(rr['meta'])
    return rr

def adjust_baselot(r):
    pluto = extract_prefixed(r,'pluto',prune=True)
    inflate_shape(pluto)
    return pluto

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

def clear_bool(r,members=None):
    """Given a dict, set all True values to 1, and delete False valuse."""
    if members is None:
        members = sorted(r.keys())
    for k in members:
        if isinstance(r[k],bool):
            if r[k]:
                r[k] = 1
            else:
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

def adjust_pluto(pluto):
    """Augment pluto struct with nice descriptive fields (in-place)."""
    if not pluto:
        return
    inflate_shape(pluto)
    pluto['bldg_count_label'] = _pluto_bldg_count_label(pluto['bldg_count'])

def adjust_acris(acris):
    if not acris:
        return
    fixdates(acris)
    amount = acris.get('amount')
    if amount is not None:
        acris['amount'] = round(amount)

def adjust_stable(stable):
    # These have been coming out of the database as float for some reason
    if not stable:
        return
    lastyear = stable.get('taxbill_lastyear')
    if lastyear is not None:
        stable['taxbill_lastyear'] = round(lastyear)

def adjust_meta(meta):
    if not meta:
        return
    clear_bool(meta)


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


