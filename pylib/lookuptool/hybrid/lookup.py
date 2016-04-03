#
# An ugly, but effective "hybrid agent" that pulls from both the 
# NYC Geoclient API, and our local database, and smooshes everything 
# together. 
#
import time

tinykeys = ('bbl','latitude','longitude')

class LookupAgent(object):

    def __init__(self,datamart,geoclient):
        self.datamart  = datamart 
        self.geoclient = geoclient 

    def get_combined_summary(self,query):
        ''' Combined geoclient + ownership summary for a given address''' 
        r,status = self.geoclient.fetch(query,tinykeys)
        bbl = int(r['bbl']) 
        summary = self.datamart.get_summary(bbl)
        summary['bbl']     = int(r['bbl']) 
        summary['geo_lat'] = "%.4f" % float(r['latitude'])
        summary['geo_lon'] = "%.4f" % float(r['longitude'])
        return summary
        

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
