#
# A mock agent for the NYC Geoclient API, which returns canned
# responses for a small set of test cases, or "not found" messages
# otherwise.
#
import time 
import simplejson as json
from .logging import log

#
# A canned list of known lookups by address tuple.
#
# Fields are exactly those in the mockfields tuple below; and the value 
# tuples are presented with the same types (str,float,float) as thse 
# fields come down in the JSON responses from the Geoclient API.
#
mockfields = ('bbl','latitude','longitude')
mockdata = {
    ('529','West 29th St','Manhattan'): ("1007017501",40.75233571801,-74.0029435297)
}

def mockrec(values):
    return dict(zip(mockfields,values))

class MockGeoClient(object):

    def __init__(self,siteurl=None,app_key=None,app_id=None):
        self.siteurl  = siteurl 
        self.app_key  = app_key
        self.app_id   = app_id

    def fetch_default(self,house_number,street_name,boro_name):
        delta = 0.01
        query = house_number,street_name,boro_name
        if query in mockdata:
            inforec = mockrec(mockdata[query])
        else:
            inforec = None
        status = {'code':200, 'time':delta}
        return inforec,status

    def fetch(self,query,fields=None):
        inforec,status = self.fetch_default(**query)
        if fields and inforec:
            tinyrec = {k:inforec.get(k) for k in fields}
            return tinyrec,status 
        else:
            return inforec,status


