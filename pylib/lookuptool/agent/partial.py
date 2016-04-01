#
# A "partial lookup" agent, the pulls information from local tables only, 
# given a BBL as the search key.  Useful for testing the local aspects of 
# the lookup service, before these results get mixed in with what we
# get from the NYC Geoclient API.
#
# BTW historically, when we had a much simpler local database, this used 
# to be the primary search agent.
#
from lookuptool.agent.base import AgentBase

class PartialAgent(AgentBase):

    def get_lookup(self,bbl):
        '''Full lookup summary per BBL.'''
        summary = self.get_summary(bbl)
        contacts  = self.get_contacts(bbl) if not summary['toobig'] else None
        buildings = self.get_buildings(bbl) if not summary['toobig'] else None
        return {
          "summary":summary,
          "contacts": contacts,
          "buildings": buildings
        }
        
    def get_contacts(self,bbl):
        '''Fetches contacts per BBL.'''
        query = \
            "select id as contact_id, registration_id, contact_type, description, corpname, contact_name, business_address " + \
            "from hard.contact_info where bbl = %d order by registration_id, contact_rank;" 
        recs = self.fetch_recs(query,bbl)
        return recs

    def get_buildings(self,bbl):
        '''Fetches distinct building registrations per BBL.'''
        query = "select * from hard.registrations where bbl = %d order by street_name, house_number;"
        recs = self.fetch_recs(query,bbl)
        for r in recs:
            r['last_date'] = str(r['last_date'])
            r['end_date']  = str(r['end_date'])
        return recs

    # Yes, we return the BBL we're selecting on back in the response dict;
    # this makes it easier to pass around the UI (otherwise, many of our
    # display functions would require it as a separate parameter).
    def get_summary(self,bbl):
        '''Fetches summary data per BBL.'''
        query = \
            "select building_count, contact_count, boro_id, cb_id, geo_lat, geo_lon " + \
            "from hard.property_summary where bbl = %d;"
        recs = self.fetch_recs(query,bbl)
        if len(recs):
            r = recs[0]
            r['present'] = True
            r['toobig']  = is_largeish(r) 
            r['bbl'] = bbl
            return r
        else:
            return { 
              "bbl":bbl,
              "present":False,
              "toobig":False,
              "contact_count":0,
              "building_count":0,
            }


# A rough guess as to whether the entire result set would be too large 
# for clients to grab + display in a single shot. 
def is_largeish(r):
    return False;
    return r['contact_count'] + r['building_count'] > 40;

