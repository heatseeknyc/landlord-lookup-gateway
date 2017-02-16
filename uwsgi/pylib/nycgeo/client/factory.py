from nycgeo.client.simple import SimpleGeoClient
from nycgeo.client.mock import MockGeoClient

def instance(config,mock=False):
    if mock:
        return MockGeoClient(**config)
    else:
        return SimpleGeoClient(**config)

