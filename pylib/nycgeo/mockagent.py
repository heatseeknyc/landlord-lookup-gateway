#
# A mock agent for the NYC Geoclient API, which returns canned
# responses for a small set of test cases, or "not found" messages
# otherwise.
#
import time 
import simplejson as json
from .logging import log
from lookuptool.geoutils import split_address

#
# A canned list of known lookups by address tuple.
# LHS: address tuple in standard form
# RHS: bbl,bin,lat,lon 
#
mockdata = {
    ('529','West 29th St','Manhattan') : ("1007017501","1089360",40.7523357180,-74.0029435297),
    ('1','West 72nd St','Manhattan')   : ("1011250025","1028637",40.7767815597,-73.9761519317)
}

# Converts tuple of lookup values on the RHS in the above table
# into a mock record in the same form of a valid Geoclient response, 
# but restricted to just these fields of interest.
def mockrec(values):
    _bbl,_bin,lat,lon = values
    return {
        "bbl": _bbl,
        "latitude":lat,
        "longitude":lat,
        "giBuildingIdentificationNumber1": _bin 
    }

class MockGeoClient(object):

    def __init__(self,siteurl=None,app_key=None,app_id=None):
        self.siteurl  = siteurl 
        self.app_key  = app_key
        self.app_id   = app_id

    def fetch_default(self,rawaddr):
        delta = 0.01
        query = split_address(rawaddr) 
        print(":: query = %s" % str(query))
        if query in mockdata:
            inforec = mockrec(mockdata[query])
        else:
            inforec = None
        status = {'code':200, 'time':delta}
        return inforec,status

    def fetch(self,rawaddr,fields=None):
        inforec,status = self.fetch_default(rawaddr)
        if fields and inforec:
            tinyrec = {k:inforec.get(k) for k in fields}
            return tinyrec,status 
        else:
            return inforec,status


