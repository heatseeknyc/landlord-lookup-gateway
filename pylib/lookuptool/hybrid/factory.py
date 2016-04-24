from nycgeo.client import SimpleGeoClient
from ..agent import DataClient
from .lookup import LookupAgent

def instance(dataconf,geoconf):
    dataclient = DataClient(**dataconf) 
    geoclient  = SimpleGeoClient(**geoconf)
    return LookupAgent(dataclient,geoclient)

