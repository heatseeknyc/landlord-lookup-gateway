import nycgeo.factory
from ..agent import DataMartAgent
from .lookup import LookupAgent

def instance(dataconf,geoconf,mock=False):
    datamart = DataMartAgent(**dataconf) 
    geoclient = nycgeo.factory.instance(geoconf,mock)
    return LookupAgent(datamart,geoclient)

