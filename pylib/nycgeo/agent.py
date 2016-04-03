#
# An extremely simple interface to the NYC Geoclient API, providing just
# the query functionality we need.
#
import requests, time 
import simplejson as json
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


    def fetch_default(self,house_number,street_name,boro_name):
        base = '/geoclient/v1/address.json'
        query = '&'.join([
            'houseNumber=%s' % house_number,
            'street=%s' % street_name,
            'borough=%s' % boro_name 
        ])
        r,delta = self.authget(base,query)
        status = {
            'code': r.response_code,
            'time': delta
        }
        if r.status_code == 200:
            d = json.loads(r.content)
            inforec = d.get('inforec')
        else:
            inforec = None
        return inforec,status


    def fetch(self,query,fields=None):
        inforec,status = self.fetch_default(**query)
        if fields and inforec :
            tiny = {k:inforec.get(k) for k in fields)
            return tinyrec,status 
        else:
            return inforec,status


