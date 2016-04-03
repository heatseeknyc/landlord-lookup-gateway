from nycgeo.agent import SimpleGeoClient 
from nycgeo.mockagent import MockGeoClient 

def instance(config,mock=False):
    if mock:
        return MockGeoClient(**config)
    else:
        return SimpleGeoClient(**config)

