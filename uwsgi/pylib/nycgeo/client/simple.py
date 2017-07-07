"""
A simple interface to the NYC Geoclient API, providing just the query
functionality we need, with occasional reformatting as needed.
"""
import requests, time
import simplejson as json
from nycgeo.utils.address import split_address
from common.logging import log

default_siteurl = 'https://api.cityofnewyork.us'

class SimpleGeoClient(object):

    def __init__(self,siteurl=default_siteurl,app_key=None,app_id=None,verify=True):
        self.siteurl  = siteurl
        self.app_key  = app_key
        self.app_id   = app_id
        self.verify   = verify

    def get(self,suburl):
        log.info("siteurl = %s" % self.siteurl)
        log.info("suburl = %s" % suburl)
        t0 = time.time()
        r = requests.get((self.siteurl+suburl).encode('utf-8'),verify=self.verify)
        t1 = time.time()
        dt = 1000*(t1-t0)
        log.info("status = %d in %.2f ms" % (r.status_code,dt))
        for k,v in r.headers.items():
            log.info("header - '%s': '%s'" % (k,v))
        return r,dt

    def authget(self,base,query):
        auth = 'app_id=%s&app_key=%s' % (self.app_id,self.app_key)
        return self.get(base + '?' + query + '&' + auth)

    def fetch_default(self,param):
        base = '/geoclient/v1/address.json'
        query = namedtuple2query(param)
        log.debug("query = %s" % query)
        return self.authget(base,query)

    def fetch(self,rawaddr):
        """
        The preferred access route to the Geoclient.  Returns a tuple of (status,response).
        :status: isa dict of response status 
        :response: the response struct (possibly None)
        """
        param = split_address(rawaddr)
        if param is None:
            response = None
            status   = {"code":None, "time":0.001, "error":"invalid address"}
            return status,response
        r,delta = self.fetch_default(param)
        status = { 'code': r.status_code, 'time': delta }
        if r.status_code == 200:
            d = json.loads(r.content)
            inforec = d.get('address')
        else:
            inforec = None
        return status,inforec

    def fetch_tiny(self,rawaddr):
        log.debug("rawaddr = '%s'" % rawaddr)
        status,response = self.fetch(rawaddr)
        log.debug("status   = %s" % status)
        log.debug("response = %s" % response)
        if response is None:
            return status,None
        else:
            tinyrec = make_tiny(response)
            return status,tinyrec


def _encode(s):
    return '' if s is None else s.replace(' ','%20')

def namedtuple2query(named):
    d = named._asdict()
    return '&'.join(['%s=%s' % (_encode(k),_encode(v)) for k,v in d.items()])

def make_tiny(r):
    # fields = ('bbl','buildingIdentificationNumber','message')
    # return {k:r.get(k) for k in fields}
    tiny = {}
    tiny['bbl'] = r.get('bbl')
    tiny['bin'] = r.get('buildingIdentificationNumber')
    message = r.get('message')
    if message is not None:
        tiny['message'] = message
    return tiny




# deprecated 
def find_bin(buildings):
    rawbin = (r['giBuildingIdentificationNumber'] for r in buildings)
    allbin = set(rawbin)
    if len(allbin) == 0:
        raise ValueError("invalid response struct")
    if len(allbin) == 1:
        return list(allbin)[0]
    else:
        return None


