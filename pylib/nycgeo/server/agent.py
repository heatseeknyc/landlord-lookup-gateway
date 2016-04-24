from nycgeo.collections import OrderedLookup
from nycgeo.utils.address import split_address 

class GeoServerMockAgent(object):

    def __init__(self,mockdata):
        self.load_recs(mockdata)

    def load_recs(self,mockdata):
        pairs = ((split_address(r['address']),r['response']) for r in mockdata)
        self.data = OrderedLookup(pairs)

    def lookup(self,param):
        if param in self.data:
            record = self.data.get(param)
            return {"address":record}
        else:
            return {"address":{"message":"not found"}}


