#
# An unimaginatively named "data client" agent that provides simple accessors 
# for the record pulls we're likely to need in our UI (along with a few other
# secret ones for diagnosis).
#
from .base import AgentBase
from common.logging import log
import simplejson as json

class DataClient(AgentBase):

    # We return the BBL we're selecting on, along with the boro_id, 
    # along with the response dict, for the convenience of frontend 
    # handlers (which otherwise would have to pass these along as
    # separate parameters for what they need to do).
    #
    # Special note about the WHERE clause below:  Basically it's saying 
    # "first try to match on BBL and BIN if both present; otherwise just 
    # match on BBL with an empty BIN."  Which is precisely our intent:  
    # the BIN key disambiguates building-specific (HPD+DHCR), so if the BIN 
    # is present, we want to disambiguate those rows.  If it isn't, then we 
    # just need the taxbill columns (and the DHCR+HPD columns will be NULL).
    #
    # In either case, we're guaranteed to have at most 1 row match in response.
    def get_summary(self,_bbl,_bin):
        '''Full ownership summary (Taxbill,DHRC,HPD) for a BBL+BIN pair.'''
        log.debug("bbl = %d, bin = %d" % (_bbl,_bin))
        query = "select * from hard.property_summary where bbl = %d and (bin = %d or bin is null)";
        r = self.fetchone(query,_bbl,_bin)
        log.debug("r = %s" % str(r))
        return make_summary(r) if r is not None else None

    def get_contacts(self,_bbl,_bin):
        '''HPD contacts per BBL'''
        query = \
            "select contact_id, registration_id, contact_type, description, corpname, contact_name, business_address " + \
            "from hard.contact_info where bbl = %d and bin = %d order by registration_id, contact_rank;"
        return self.fetch_recs(query,_bbl,_bin)


def make_summary(r):
    taxbill = {
        'active_date': str(r['taxbill_active_date']),
        'owner_address': expand_address(r['taxbill_owner_address']),
        'owner_name': r['taxbill_owner_name'],
    }
    building = {
        'lon_ctr': r['building_lon_ctr'],
        'lat_ctr': r['building_lat_ctr'],
        'radius': r['building_radius'],
        'points': json.loads(r['building_points']),
        'parts': json.loads(r['building_parts']),
    }
    return  {
        "taxbill": taxbill,
        "building": building,
        "nychpd_contacts": cast_as_int(r['contact_count']) ,
        "dhcr_active": bool(r.get('dhcr_active'))
    }

# Splits the taxbill owner addresss on the embedded '\\n' string 
# (literally '\'+'\'+'n') from an incoming string, which we take to 
# be an encoding of "\n"; e.g:
#
#   e.g. 'DAKOTA INC. (THE)\\n1 W. 72ND ST.\\nNEW YORK , NY 10023-3486'
#
# then strips whitespace from the resulting terms, and returns a nice 
# list struct.
def expand_address(s):
    if s is None:
        return None
    terms = s.split('\\n')
    return [t.strip() for t in terms]

def cast_as_int(x):
    return 0 if x is None else int(x)

