import nycgeo.factory
from ..agent import DataClient
from .lookup import LookupAgent

def instance(dataconf,geoconf,mock=False):
    datamart = DataClientAgent(**dataconf) 
    geoclient = nycgeo.factory.instance(geoconf,mock)
    return LookupAgent(datamart,geoclient)

