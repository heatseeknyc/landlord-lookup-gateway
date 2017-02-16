from nycgeo.collections import OrderedLookup
from nycgeo.utils.address import split_address
from common.logging import log

class GeoServerMockAgent(object):

    def __init__(self,mockdata):
        self.load_recs(mockdata)

    def load_recs(self,mockdata):
        pairs = ((split_address(r['address']),r['nycgeo']) for r in mockdata)
        self.data = OrderedLookup(pairs)

    def lookup(self,param):
        log.debug("param = %s" % str(param))
        if param in self.data:
            record = self.data.get(param)
            return {"address":record}
        else:
            return {"address":{"message":"unknown address"}}


