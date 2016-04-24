#
# A simple interface to the NYC Geoclient API, providing just the query 
# functionality we need, along with some necessary pivoting of response 
# structs to make the data easier to work with internally. 
#
import requests, time 
import simplejson as json
from nycgeo.utils.address import split_address
from nycgeo.utils.pivot import pivot_nycgeo
from nycgeo.logging import log

default_siteurl = 'https://api.cityofnewyork.us'

class SimpleGeoClient(object):

    def __init__(self,siteurl=default_siteurl,app_key=None,app_id=None):
        self.siteurl  = siteurl 
        self.app_key  = app_key
        self.app_id   = app_id

    def get(self,suburl):
        log.info("siteurl = %s" % self.siteurl)
        log.info("suburl = %s" % suburl)
        t0 = time.time()
        r = requests.get((self.siteurl+suburl).encode('utf-8'))
        t1 = time.time()
        dt = 1000*(t1-t0)
        log.info("status = %d in %.2f ms" % (r.status_code,dt))
        return r,dt

    def authget(self,base,query):
        auth = 'app_id=%s&app_key=%s' % (self.app_id,self.app_key) 
        return self.get(base + '?' + query + '&' + auth)

    def fetch_default(self,param):
        base = '/geoclient/v1/address.json'
        query = namedtuple2query(param)
        print(":: query = %s" % query)
        return self.authget(base,query)

    def fetch(self,rawaddr):
        param = split_address(rawaddr)
        if param is None:
            response = None
            status   = {"code":None, "time":0.001, "error":"invalid address"}
            return response,status
        r,delta = self.fetch_default(param)
        status = { 'code': r.status_code, 'time': delta }
        if r.status_code == 200:
            d = json.loads(r.content)
            inforec = d.get('address')
        else:
            inforec = None
        return inforec,status

    def fetch_tiny(self,rawaddr):
        response,status = self.fetch(rawaddr)
        if response:
            tinyrec = make_tiny(response) 
            return tinyrec,status 
        else:
            return response,status

    def __fetch_norm(self,rawaddr):
        inforec,status = self.fetch(rawaddr)
        if inforec:
            normrec = pivot_nycgeo(inforec)
            return normrec,status 
        else:
            return inforec,status



def _encode(s):
    return '' if s is None else s.replace(' ','%20')

def namedtuple2query(named):
    d = named._asdict()
    return '&'.join(['%s=%s' % (_encode(k),_encode(v)) for k,v in d.items()])

def make_tiny(r):
    if 'message' in r:
        return {'message':r['message']}
    fields = ('bbl','buildingIdentificationNumber','latitude','longitude')
    return {k:r.get(k) for k in fields}


#
# Deprecatd Stuff
#


def find_bin(buildings):
    rawbin = (r['giBuildingIdentificationNumber'] for r in buildings)
    allbin = set(rawbin)
    if len(allbin) == 0:
        raise ValueError("invalid response struct")
    if len(allbin) == 1:
        return list(allbin)[0]
    else:
        return None


