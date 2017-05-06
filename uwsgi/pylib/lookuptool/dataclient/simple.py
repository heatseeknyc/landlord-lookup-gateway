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
        '''Full ownership summary (Taxbill,DHRC,HPD) for a BBL+BIN pair.'''
        log.debug("bbl = %s, bin = %s" % (_bbl,_bin))
        query = "select * from hard.property_summary where bbl = %s and (bin = %s or bin is null)";
        r = self.fetchone(query,_bbl,_bin)
        log.debug("r = %s" % str(r))
        return make_summary(r) if r is not None else None

    def get_contacts(self,_bbl,_bin):
        '''HPD contacts per BBL'''
        query = \
            "select contact_id, registration_id, contact_type, description, corpname, contact_name, business_address " + \
            "from hard.contact_info where bbl = %s and bin = %s order by registration_id, contact_rank;"
        return self.fetch_recs(query,_bbl,_bin)

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

def extract_prefixed(r,prefix,tojson=None,collapse=True):
    prefix_ = prefix+'_'
    tojson = set(tojson) if tojson is not None else set()
    tags = sorted(k for k in r.keys() if k.startswith(prefix_))
    n = len(prefix_)
    x = {_trunc(k,n):deepcopy(r[k]) for k in tags}
    if collapse and all(v is None for v in x.values()):
        return None
    return x

def augment_pluto(p):
    """Augment pluto struct with nice descriptive fields (in-place)."""
    if not p:
        return
    n = p['bldg_count']
    if n == 0:
        p['describe_count'] = "A vacant lot"
    else:
        s = 's' if n > 1 else ''
        p['describe_count'] = "A lot with %d building%s" % (n,s)

def make_summary(r):
    stable = extract_prefixed(r,'stable')
    building = extract_prefixed(r,'building')
    pluto = extract_prefixed(r,'pluto')
    if building:
        applymems(building,jsonify,['parts','points'])
    if pluto:
        applymems(pluto,jsonify,['parts','points'])
        augment_pluto(pluto)
    return  {
        'pluto': pluto,
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

