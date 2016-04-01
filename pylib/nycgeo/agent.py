import requests 
from .logging import log

default_siteurl = 'https://api.cityofnewyork.us'

class Agent(object):

    def __init__(self,siteurl=default_siteurl,app_key=None,app_id=None):
        self.siteurl  = siteurl 
        self.app_key  = app_key
        self.app_id   = app_id

    def get(self,suburl):
        log.info("suburl = %s" % suburl)
        r = requests.get((self.siteurl+suburl).encode('utf-8'))
        log.info("status = %d" % r.status_code)
        return r

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
        return self.fetch(base,query)


