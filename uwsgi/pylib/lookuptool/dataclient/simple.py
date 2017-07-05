"""
An unimaginatively named "data client" agent that provides simple accessors
for the record pulls we're likely to need in our UI (along with a few other
secret ones for diagnosis).
"""
from .base import AgentBase
from common.logging import log
from copy import deepcopy
import simplejson as json

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
    def get_building(self,_bbl,_bin):
        log.debug("bbl = %s, bin = %s" % (_bbl,_bin))
        if _bbl is None:
            return []
        if _bin is None:
            query = "select * from hard.building where bbl = %s and in_pluto order by bin, doitt_id"
            r = self.fetch_recs(query,_bbl)
            log.debug("fetched type(r) = %s" % type(r))
            log.debug("fetched r = %s" % r)
            return r
        else:
            query = "select * from hard.building where bbl = %s and bin = %s and in_pluto order by doitt_id"
            r = self.fetch_recs(query,_bbl,_bin)
            log.debug("fetched type(r) = %s" % type(r))
            log.debug("fetched r = %s" % r)
            return r

    """
    We return the BBL we're selecting on, along with the boro_id,
    along with the response dict, for the convenience of frontend
    handlers (which otherwise would have to pass these along as
    separate parameters for what they need to do).

    Special note about the WHERE clause below:  Basically it's saying
    "first try to match on BBL and BIN if both present; otherwise just
    match on BBL with an empty BIN."  Which is precisely our intent:
    the BIN key disambiguates building-specific (HPD+DHCR), so if the BIN
    is present, we want to disambiguate those rows.  If it isn't, then we
    just need the taxbill columns (and the DHCR+HPD columns will be NULL).

    In either case, we're guaranteed to have at most 1 row match in response.
    """
    def get_summary(self,_bbl,_bin):
        """
        Full taxlot+building summary for a BBL+BIN pair.  The whole idea of this accessors is
        that it does all the internal switching necessary to give you both taxlot and building
        attributes depending on whether you have both identifiers (BBL,BIN) or just a BBL - and
        works as you would expected for vacant lots as well as multi-building lots.  Of course,
        you do need to supply at least a valid BBL.
        """
        log.debug("bbl = %s, bin = %s" % (_bbl,_bin))
        # query = "select * from deco.property_summary where bbl = %s and (bin = %s or bin is null)";
        query,args = make_summary_query(_bbl,_bin)
        log.debug("query = [%s]" % query)
        log.debug("args = %s" % str(args))
        # r = self.fetchone(query,_bbl,_bin)
        r = self.fetchone(query,*args)
        log.debug("r = %s" % str(r))
        return expand_summary(r) if r is not None else None

    def get_contacts(self,_bbl,_bin):
        '''HPD contacts per BBL'''
        query = \
            "select contact_id, registration_id, contact_type, description, corpname, contact_name, business_address " + \
            "from hard.contact_info where bbl = %s and bin = %s order by registration_id, contact_rank;"
        return self.fetch_recs(query,_bbl,_bin)

    def get_buildings(self,_bbl):
        '''Building IDs + shapes per BBL'''
        query = \
            "select bin,doitt_id,lat_ctr,lon_ctr,radius,parts,points " + \
            "from hard.pluto_building where bbl = %s order by doitt_id";
        r = self.fetch_recs(query,_bbl)
        log.debug("r = %s" % str(r))
        if r:
            [inflate_shape(_) for _ in r]
        return r

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

def extract_taxbill(r):
    if r.get('taxbill_owner_name') is None:
        return None
    active_date = r['taxbill_active_date']
    owner_address = r['taxbill_owner_address']
    return {
        'active_date': str(active_date) if active_date else None,
        'owner_address': expand_address(owner_address) if owner_address else [],
        'owner_name': r['taxbill_owner_name'],
    }

def _trunc(k,n):
    """Simply truncates first :n characters fron the (presumably) well-formed dict :key
    if possible to do so; otherwise, throws an exception relevant to the particular
    function we're calling it from."""
    if len(k) > n:
        return k[n:]
    else:
        raise ValueError("invalid key '%s' relative to prefix '%s'" (tag,prefix))

def extract_prefixed(r,prefix,collapse=True,prune=False):
    prefix_ = prefix+'_'
    x,n = {},len(prefix_)
    tags = sorted(k for k in r.keys() if k.startswith(prefix_))
    for k in tags:
        j = _trunc(k,n)
        x[j] = deepcopy(r[k])
        if prune:
            del r[k]
    if collapse and all(v is None for v in x.values()):
        return None
    return x

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

_shape_fields = ('lat_ctr','lon_ctr','radius','points','parts')
def extract_shape(r):
    return extract_fields(r,_shape_fields)


def inflate_shape(r):
    if r:
        applymems(r,jsonify,['parts','points'])

def _pluto_bldg_count_label(n):
    if n == 0:
        return "A vacant lot"
    else:
        s = 's' if n > 1 else ''
        return "A lot with %d building%s" % (n,s)

def augment_pluto(p):
    """Augment pluto struct with nice descriptive fields (in-place)."""
    if not p:
        return
    p['bldg_count_label'] = _pluto_bldg_count_label(p['bldg_count'])

def stagger_taxlot(r):
    """Invasively 'staggers' a database response to a taxlot query. returning
    a new bilevel dict and mangling the old one beyond recognition."""
    if r is None:
        return None
    rr = {}
    rr['pluto'] = extract_prefixed(r,'pluto',prune=True)
    rr['acris'] = extract_prefixed(r,'acris',prune=True)
    rr['meta'] = deepcopy(r)
    inflate_shape(rr['pluto'])
    return rr

def expand_summary(r):
    stable = extract_prefixed(r,'stable')
    building = extract_prefixed(r,'building')
    pluto = extract_prefixed(r,'pluto')
    taxlot = extract_shape(pluto)
    inflate_shape(building)
    inflate_shape(taxlot)
    if pluto:
        augment_pluto(pluto)
    return  {
        'pluto': pluto,
        'taxlot': taxlot,
        'stable': stable,
        'building': building,
        'nychpd_count': r.get('nychpd_count'),
    }


def applymems(r,callf,keys):
    for k in keys:
        if k in r:
            r[k] = callf(r[k])

def jsonify(x):
    return None if x is None else json.loads(x)

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

def cast_as_int(x):
    return 0 if x is None else int(x)

