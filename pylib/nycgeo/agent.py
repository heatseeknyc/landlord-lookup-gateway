import requests, time 
from .logging import log

default_siteurl = 'https://api.cityofnewyork.us'

class Agent(object):

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

    def fetch(self,base,query):
        auth = 'app_id=%s&app_key=%s' % (self.app_id,self.app_key) 
        return self.get(base + '?' + query + '&' + auth)


    # 'houseNumber=314&street=west+100+st&borough=manhattan'
    def fetch_address(self,house_number,street_name,boro_name):
        base = '/geoclient/v1/address.json'
        query = '&'.join([
            'houseNumber=%s' % house_number,
            'street=%s' % street_name,
            'borough=%s' % boro_name 
        ])
        r,dt = self.fetch(base,query)
        if r.status_code == 200:
            return json.loads(r.content),dt
        else:
            errmsg = "status %s" % r.status_code
            return {'error':errmsg},dt


