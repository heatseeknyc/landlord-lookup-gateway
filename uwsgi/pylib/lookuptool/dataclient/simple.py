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
    # match on BBL with an empty BIN."  Which is precisely our intent:  
    # the BIN key disambiguates building-specific (HPD+DHCR), so if the BIN 
    # is present, we want to disambiguate those rows.  If it isn't, then we 
    # just need the taxbill columns (and the DHCR+HPD columns will be NULL).
    #
    # In either case, we're guaranteed to have at most 1 row match in response.
    #
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
        recs = self.fetch_recs(query,_bbl,_bin)
        return recs


