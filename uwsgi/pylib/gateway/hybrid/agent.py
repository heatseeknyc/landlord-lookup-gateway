"""
An ugly, but effective "hybrid agent" that pulls from both the
NYC Geoclient API, and our local database, and smooshes everything
together.
"""
import re
from nycprop.identity import is_valid_bbl, is_valid_bin
from gateway.util.address import fix_borough_name
from common.logging import log


class LookupAgent(object):

    def __init__(self,dataclient,geoclient):
        self.dataclient = dataclient
        self.geoclient  = geoclient

    def dispatch(self,endpoint,*args):
        """The preferred entry point to our endpoints."""
        if endpoint == 'lookup':
            return self.get_lookup(*args)
        if endpoint == 'buildings':
            # this will raise, presently
            return self.get_buildings(*args)
        return {'error':'invalid endpoint'}

    def resolve_address(self,rawaddr):
        log.info(":: rawaddr  = '%s'" % rawaddr)
        normaddr = fix_borough_name(rawaddr)
        log.debug(":: normaddr = '%s'" % normaddr)
        keytup,status = self.geoclient.fetch_tiny(normaddr)
        log.debug(":: status = %s " % status)
        log.debug(":: response = %s" % keytup)
        return keytup,status

    #
    # Note that the next two handlers are nearly congruent (once we decide what
    # our BBL is), but have subtly different error handling.
    #

    def get_lookup_by_bbl(self,bbl):
        log.debug(":: bbl = %s" % bbl)
        if not is_valid_bbl(bbl):
            raise ValueError("invalid bbl '%s'" % str(bbl))
        taxlot = self.dataclient.get_taxlot(bbl)
        keytup = {'bbl':bbl,'bin':None}
        if taxlot is None:
            # This means the user gave us a BBL, but it's not recognized. 
            return {'keytup':keytup,'error':'bbl not recognized'}
        else:
            return {'keytup':keytup,'taxlot':taxlot}

    def get_lookup_by_rawaddr(self,rawaddr):
        log.debug(":: rawaddr = '%s'" % rawaddr)
        keytup,status = self.resolve_address(rawaddr)
        if status != 200:
            return {'error':'no response from geoclient'}

        # Geoclient returned something, but had no 'address' member. 
        # So basically it's barfing at us. 
        if keytup is None:
            return {'error':'malformed input'}

        # If we get here then we still might have a valid address, but if not,
        # at least the Geoclient will provide some explanation for us.
        bbl = keytup.get('bbl')
        if bbl is None:
            message = keytup.get('message')
            if message is None:
                message = "[malformed response from Geoclient]"
            error = "cannot resolve address"
            return {'error':error,'message':message}

        # Successful address resolution - perhaps with caveats. 
        if 'message' in keytup:
            # If we get 'message' at this stage, it's interepreted as a warning
            # or caveat about the address, most likely of no use (and perhaps only confusing)
            # to the user.  We'll pass it along anyway, but most likely it won't be displayed.
            log.warn(":: bbl=%s, message=[%s]" % (bbl,keytup['message']))

        taxlot = self.dataclient.get_taxlot(bbl)
        if taxlot is None:
            # If we don't get a taxlot lookup at this stage, this means the Geoclient sent 
            # us a BBL, but it's not in our combined database.  This would be really weird, 
            # if it ever happens.  However, we'll let the frontend determine how to handle 
            # that condition.
            return {'keytup':keytup,'error':'bbl not recognized'}
        else:
            # Generic valid lookup. 
            return {'keytup':keytup,'taxlot':taxlot}


    def get_lookup(self,query):
        ''' Combined geoclient + ownership summary for a given address'''
        log.debug(":: query = '%s'" % query)
        if query is None:
            raise ValueError("invalid usage - null query object")
        if _intlike(query):
            bbl = int(query)
            if is_valid_bbl(bbl):
                return self.get_lookup_by_bbl(bbl)
            else:
                return { 'error':"invalid bbl" }
        else:
            return self.get_lookup_by_rawaddr(query)

    def get_contacts(self,bbl):
        contacts = self.dataclient.get_contacts(bbl)
        return {"contacts":contacts}

    def get_buildings(self,query):
        # print(":: query = [%s]" % query)
        keytup = split_buildings_query(query)
        # print(":: keytup = %s" % str(keytup))
        if keytup is None:
            return {'error':'invalid query'}
        _bbl,_bin = keytup
        if not is_valid_bbl(_bbl):
            return {'error':'invalid bbl'}
        if _bin is not None and not is_valid_bin(_bin):
            return {'error':'invalid bin'}
        buildings = self.dataclient.get_building(_bbl,_bin)
        return {'buildings':buildings}


#
# Support functions
#

_querypat = re.compile('(\d+)(,(\d+))?$')
def split_buildings_query(query):
    if query is None:
        raise ValueError('invalid usage')
    m = re.match(_querypat,query)
    if m:
        _bbl,_bin = m.group(1),m.group(3)
        # print("bbl = %s" % _bbl)
        # print("bin = %s" % _bin)
        _bbl = int(_bbl)
        _bin = int(_bin) if _bin else None
        return _bbl,_bin
    else:
        return None

_intpat = re.compile('^\d+$')
def _intlike(s):
    return re.match(_intpat,s)

def softint(s):
    return int(s) if s is not None else None




# deprecated 
def make_tiny(r):
    """
    Returns a canonicalized form of our response from the the 'geoclient' agent.
    """
    tiny = {
        'bbl': softint(r.get('bbl')),
        'bin': softint(r.get('buildingIdentificationNumber')),
    }
    if 'message' in r:
        tiny['message'] = r['message']
    return tiny



