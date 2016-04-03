#
# A generic "data mart" agent that provides simple-to-use accessors for 
# any of the data pulls we're likely to do on our little data warehouse,
# as such.
#
from lookuptool.agent.base import AgentBase

class DataMartAgent(AgentBase):

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
        
    # We return the BBL we're selecting on back in the response dict;
    # this makes it easier to pass around the UI (otherwise, many of our
    # display functions would require it as a separate parameter).
    def get_summary(self,bbl):
        '''Joint taxbill+HPD summary data per BBL'''
        query = \
            "select taxbill_owner_name, taxbill_owner_address, taxbill_active_date, " + \
            "building_count, contact_count, boro_id " + \
            "from hard.property_summary where bbl = %d;"
        recs = self.fetch_recs(query,bbl)
        if len(recs):
            r = recs[0]
            r['bbl'] = bbl
            r['present'] = True
            r['toobig']  = is_largeish(r) 
            r['taxbill_active_date'] = str(r['taxbill_active_date'])
            r['taxbill_owner_address']  = expand_address(r['taxbill_owner_address'])
            return r
        else:
            return { 
              "bbl":bbl,
              "present":False,
              "toobig":False,
              "contact_count":0,
              "building_count":0,
            }

    def get_details(self,bbl):
        contacts  = self.get_contacts(bbl)
        buildings = self.get_buildings(bbl)
        return {
          "contacts": contacts,
          "buildings": buildings
        }

    def get_contacts(self,bbl):
        '''HPD contacts per BBL'''
        query = \
            "select id as contact_id, registration_id, contact_type, description, corpname, contact_name, business_address " + \
            "from hard.contact_info where bbl = %d order by registration_id, contact_rank;" 
        recs = self.fetch_recs(query,bbl)
        return recs

    def get_buildings(self,bbl):
        '''Distinct HPD building registrations per BBL'''
        query = "select * from hard.registrations where bbl = %d order by street_name, house_number;"
        recs = self.fetch_recs(query,bbl)
        for r in recs:
            r['last_date'] = str(r['last_date'])
            r['end_date']  = str(r['end_date'])
        return recs


# A rough guess as to whether the entire result set would be too large 
# for clients to grab + display in a single shot. 
def is_largeish(r):
    return False;
    return r['contact_count'] + r['building_count'] > 40;

#
# Splits taxbill owner addresss on the embedded '\\n' string (as in, the
# character '\' + 'n'), and strips whitespace of a resultant terms. 
#
#   e.g. "DAKOTA INC. (THE)\\n1 W. 72ND ST.\\nNEW YORK , NY 10023-3486"
#
def expand_address(s):
    if s is None:
        return None
    terms = s.split('\\n')
    return [t.strip() for t in terms]

