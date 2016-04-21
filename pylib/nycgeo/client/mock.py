#
# A mock agent for the NYC Geoclient API, which returns canned
# responses for a small set of test cases, or "not found" messages
# otherwise.
#
from lookuptool.geoutils import split_address
from nycgeo.logging import log
from .simple import SimpleGeoClient

class MockGeoClient(SimpleGeoClient):

    def fetch_default(self,rawaddr):
        raise RuntimeError("not implemented in mock client")

    def fetch(self,rawaddr):
        query = rawaddr
        if query in self._mockdata:
            inforec = mockrec(tuple(self._mockdata[query]))
        else:
            inforec = None
        status = {'code':200, 'time':0.01}
        return inforec,status


# Converts tuple of lookup values on the right-hand side of our mockup 
# struct into a mock record in the same format as returned by a valid 
# Geoclient response, but restricted to just these fields of interest.
def mockrec(values):
    _bbl,_bin,lat,lon = values
    return {
        "bbl": _bbl,
        "latitude":lat,
        "longitude":lon,
        "giBuildingIdentificationNumber1": _bin 
    }

