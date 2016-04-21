#
# A simple interface to the NYC Geoclient API, providing just the query 
# functionality we need, along with some necessary pivoting of response 
# structs to make the data easier to work with internally. 
#
import requests, time 
import simplejson as json
from lookuptool.geoutils import split_address
from nycgeo.utils.pivot import pivot_nycgeo
from nycgeo.logging import log

default_siteurl = 'https://api.cityofnewyork.us'

class SimpleGeoClient(object):

    def __init__(self,siteurl=default_siteurl,app_key=None,app_id=None):
        self.siteurl  = siteurl 
        self.app_key  = app_key
        self.app_id   = app_id

    def get(self,suburl):
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

    def fetch_default(self,rawaddr):
        house,street,boro = split_address(rawaddr)
        base = '/geoclient/v1/address.json'
        query = '&'.join([
            'houseNumber=%s' % house,
            'street=%s' % street,
            'borough=%s' % boro
        ])
        return self.authget(base,query)

    def fetch(self,rawaddr):
        r,delta = self.fetch_default(rawaddr)
        status = {
            'code': r.status_code,
            'time': delta
        }
        if r.status_code == 200:
            d = json.loads(r.content)
            inforec = d.get('address')
        else:
            inforec = None
        return inforec,status

    def fetch_norm(self,rawaddr):
        inforec,status = self.fetch(rawaddr)
        if inforec:
            normrec = pivot_nycgeo(inforec)
            return normrec,status 
        else:
            return inforec,status

    def fetch_tiny(self,rawaddr):
        inforec,status = self.fetch_norm(rawaddr)
        if inforec:
            tinyrec = make_tiny(inforec) 
            return tinyrec,status 
        else:
            return inforec,status





def find_bin(buildings):
    rawbin = (r['giBuildingIdentificationNumber'] for r in buildings)
    allbin = set(rawbin)
    if len(allbin) == 0:
        raise ValueError("invalid response struct")
    if len(allbin) == 1:
        return list(allbin)[0]
    else:
        return None

def make_tiny(r):
    return {
        "bin" : find_bin(r['buildings']),
        "bbl" : int(r['taxlot']['bbl']),
        "geo_lat" : r['taxlot']['latitude'],
        "geo_lon" : r['taxlot']['longitude'],
    }



