#
# An unimaginatively named "data client" agent that provides simple accessors 
# for the record pulls we're likely to need in our UI (along with a few other
# secret ones for diagnosis).
#
from .base import AgentBase
from common.logging import log

class DataClient(AgentBase):

        
    # We return the BBL we're selecting on, along with the boro_id, 
    # along with the response dict, for the convenience of frontend 
    # handlers (which otherwise would have to pass these along as
    # separate parameters for what they need to do).
    #
    # Special note about the WHERE clause below:  Basically it's saying 
    # "first try to match on BBL and BIN if both present; otherwise just 
    # match on BBL."  Which is of course precisely our intent:  the BIN key 
    # disambiguates building-specific (HPD+DHCR), so if the BIN is present,
    # we want to disambiguate those rows.  If it isn't, then we just need
    # the taxbill columns (and the DHCR+HPD columns will be NULL).
    #
    # In any case, due how the join that populates hard.property_summary 
    # is # structured, we're guaranteed to have at most 1 row match on 
    # this query.
    #
    def get_summary(self,_bbl,_bin):
        '''Full ownership summary (Taxbill,DHRC,HPD) for a BBL+BIN pair.'''
        log.debug("bbl = %d, bin = %d" % (_bbl,_bin))
        query = "select * from hard.property_summary where bbl = %d and bin = %d or bbl = %d"; 
        r = self.fetchone(query,_bbl,_bin,_bbl)
        log.debug("r = %s" % str(r)) 
        return make_summary(r) if r is not None else None

    def get_contacts(self,_bbl,_bin):
        '''HPD contacts per BBL'''
        query = \
            "select contact_id, registration_id, contact_type, description, corpname, contact_name, business_address " + \
            "from hard.contact_info where bbl = %d and bin = %d order by registration_id, contact_rank;" 
        recs = self.fetch_recs(query,_bbl,_bin)
        return recs


    # 
    # Deprecated stuff
    #

    def get_details(self,bbl):
        contacts  = self.get_contacts(bbl)
        buildings = self.get_buildings(bbl)
        return {
          "contacts": contacts,
          "buildings": buildings
        }


    def get_buildings(self,bbl):
        '''Distinct HPD building registrations per BBL'''
        query = "select * from hard.registrations where bbl = %d order by street_name, house_number;"
        recs = self.fetch_recs(query,bbl)
        for r in recs:
            r['last_date'] = str(r['last_date'])
            r['end_date']  = str(r['end_date'])
        return recs

    def get_everything(self,bbl):
        '''All the data that are fit to emit'''
        summary   = self.get_summary(bbl)
        contacts  = self.get_contacts(bbl)
        buildings = self.get_buildings(bbl)
        return {
          "summary": summary,
          "contacts": contacts,
          "buildings": buildings
        }


#
# Pivots raw SQL result record into a somewhat nice struct for 
# external consumption.
#
def make_summary(r):
    taxbill = { 
        'active_date': str(r['taxbill_active_date']),
        'owner_address': expand_address(r['taxbill_owner_address']),
        'owner_name': r['taxbill_owner_name'],
    }
    return  { 
        "taxbill":taxbill,
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


#
# Deprecated Stuff
#

# A rough guess as to whether the entire result set would be too large 
# for clients to grab + display in a single shot. 
def is_largeish(r):
    return False;
    return r['contact_count'] + r['building_count'] > 40;

