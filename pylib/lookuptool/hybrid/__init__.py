from nycgeo.client import SimpleGeoClient
from ..dataclient import DataClient
from .agent import LookupAgent

#
# A simple factory-ish method to generate a LookupAgent instance
# from the configuration dicts for its respective members. 
#
def instance(dataconf,geoconf):
    dataclient = DataClient(**dataconf) 
    geoclient  = SimpleGeoClient(**geoconf)
    return LookupAgent(dataclient,geoclient)

