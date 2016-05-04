#
# An ugly, but effective "hybrid agent" that pulls from both the 
# NYC Geoclient API, and our local database, and smooshes everything 
# together. 
#
from lookuptool.utils.address import fix_borough_name
from common.logging import log

tinykeys = ('bbl','latitude','longitude')

class LookupAgent(object):

    def __init__(self,dataclient,geoclient):
        self.dataclient  = dataclient 
        self.geoclient = geoclient 

    def get_lookup(self,rawaddr):
        ''' Combined geoclient + ownership summary for a given address''' 
        log.debug(":: rawaddr  = '%s'" % rawaddr)
        normaddr = fix_borough_name(rawaddr)
        log.debug(":: normaddr = '%s'" % normaddr)
        r,status = self.geoclient.fetch_tiny(normaddr)
        log.debug(":: status = %s " % status)
        log.debug(":: response = %s" % r)
        if r is None: 
            return {"error":"invalid address"}
        nycgeo = make_tiny(r)
        if 'message' in nycgeo:
            return {"nycgeo":nycgeo,"extras":None,"error":nycgeo.get('message')}
        else:
            extras = self.dataclient.get_summary(nycgeo['bbl'],nycgeo['bin'])
            return {"nycgeo":nycgeo,"extras":extras}

    def get_contacts(self,bbl):
        contacts = self.dataclient.get_contacts(bbl)
        return {"contacts":contacts}

def make_tiny(r):
    if 'message' in r:
        return {'message':r['message']}
    return {
        'bbl': int(r['bbl']),
        'bin': int(r['buildingIdentificationNumber']),
        'geo_lat': r['latitude'],
        'geo_lon': r['longitude']
    }

#
# Deprecated stuff
#

# Overlay dict values of b onto a. 
def overlay(a,b):
    for k in b:
        a[k] = b[k]

# The NYG Geoclient returns some 140 fields; we only need a small
# handful of them.
def truncate(bignyc): 
    address = bignyc['address']
    bbl = int(address['bbl'])
    geo_lat = "%.4f" % float(address['latitude'])
    geo_lon = "%.4f" % float(address['longitude'])
    return {
        "bbl":bbl,
        "geo_lat":geo_lat,
        "geo_lon":geo_lon
    }
