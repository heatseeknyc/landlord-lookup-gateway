#
# An unimaginatively named "data client" agent that provides simple accessors 
# for the record pulls we're likely to need in our UI (along with a few other
# secret ones for diagnosis).
#
from .base import AgentBase

class DataClient(AgentBase):

        
    # We return the BBL we're selecting on, along with the boro_id, 
    # along with the response dict, for the convenience of frontend 
    # handlers (which otherwise would have to pass these along as
    # separate parameters for what they need to do).
    #
    def get_summary(self,_bbl,_bin):
        '''Full ownership summary (Taxbill,DHRC,HPD) for a BBL+BIN pair.'''
        query = "select * from hard.property_summary where bbl = %d and bin = %d"; 
        r = self.fetchone(query,_bbl,_bin)
        if r:
            taxbill = { 
                'active_date': str(r['taxbill_active_date']),
                'owner_address': expand_address(r['taxbill_owner_address']),
                'owner_name': r['taxbill_owner_name'],
            }
            dhcr_active = bool(r.get('dhcr_active'))
            if r['contact_count'] is not None:
                nychpd_contacts = r['contact_count']
            else:
                nychpd_contacts = 0 
        else:
            taxbill = None
            nychpd_contacts = 0
            dhcr_active = False

        return  { 
            "taxbill":taxbill,
            "nychpd_contacts":nychpd_contacts,
            "dhcr_active":dhcr_active,
        }

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

