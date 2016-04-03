#
# An ugly, but effective "hybrid agent" that pulls from both the 
# NYC Geoclient API, and our local database, and smooshes everything 
# together. 
#
import time
from lookuptool.agent import PartialAgent 
from nycgeo.agent import SimpleGeoclient

class LookupAgent(object):

    def __init__(self,pgconf,nycgeoconf):
        self.partial = PartialAgent(**pgconf) 
        self.nycgeo  = SimpleGeoclient(**nycgeoconf) 

    def get_combined_summary(self,address):
        ''' Combined NYC Geoclient + HPD summary for a given address. ''' 
        t0 = time.time()
        bignyc,delta = self.nycgeo.fetch_address(**address)
        tiny = truncate(bignyc)
        bbl = tiny.get('bbl')
        r,delta = self.partial.get_lookup(bbl)
        overlay(r['summary'],tiny)
        t1 = time.time()
        dt = 1000*(t1-t0)
        return r,dt
        

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
