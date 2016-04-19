#
# An extremely simple interface to the NYC Geoclient API, providing just
# the query functionality we need.
#
import requests, time 
import simplejson as json
from lookuptool.geoutils import split_address
from .logging import log

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

    def fetch_default(self,query):
        house_number,street_number,boro_name = query
        base = '/geoclient/v1/address.json'
        query = '&'.join([
            'houseNumber=%s' % house_number,
            'street=%s' % street_name,
            'borough=%s' % boro_name 
        ])
        r,delta = self.authget(base,query)
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

    # Performas a "safe" fetch, whereby if the address doesn't parse
    # we simply return a nice error message in the status blurb.
    def fetch_safe(self,rawaddr):
        t = split_address(rawaddr)
        if t is not None:
            return self.fetch_query(t)
        else:
            inforec = None            
            status = {
                'error': 'invalid address',
                'code': None, 
                'time': None, 
            }
            return inforec,status


    def fetch(self,query,fields=None):
        inforec,status = self.fetch_safe(**query)
        if fields and inforec :
            tinyrec = {k:inforec.get(k) for k in fields}
            return tinyrec,status 
        else:
            return inforec,status

    def fetch_normalized(self,query,fields=None):
        bigrec,status = self.fetch(query,fields)
        pass

