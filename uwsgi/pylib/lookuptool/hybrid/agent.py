"""
An ugly, but effective "hybrid agent" that pulls from both the
NYC Geoclient API, and our local database, and smooshes everything
together.
"""
import re
from nycprop.identity import is_valid_bbl
from lookuptool.utils.address import fix_borough_name
from common.logging import log

nullish = set([1000000,2000000,3000000,4000000,5000000])


_intpat = re.compile('^\d+$')
def _intlike(s):
    return re.match(_intpat,s)

class LookupAgent(object):

    def __init__(self,dataclient,geoclient):
        self.dataclient = dataclient
        self.geoclient  = geoclient

    def resolve_address(self,rawaddr):
        log.info(":: rawaddr  = '%s'" % rawaddr)
        normaddr = fix_borough_name(rawaddr)
        log.debug(":: normaddr = '%s'" % normaddr)
        r,status = self.geoclient.fetch_tiny(normaddr)
        log.debug(":: status = %s " % status)
        log.debug(":: response = %s" % r)
        return make_tiny(r) if r else None

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
            # This is actually a weird condition: the Geoclient gave us a BBL, but none of 
            # our databases recognize it.  Should perhaps handle more forcefully.
            return {"keytup":keytup,"error":"bbl not recognized"}
        else:
            return {"keytup":keytup,"taxlot":taxlot}

        """
        keytup = {'bbl':bbl,'bin':None}
        log.debug(":: keytup = '%s'" % keytup)
        extras = self.dataclient.get_summary(keytup['bbl'],keytup['bin'])
        if 'message' in keytup:
            # If we get an error message at this stage, it's interepreted as a warning
            log.warn(":: bbl=%s, message=[%s]" % (keytup['bbl'],keytup['message']))
            return {'keytup':keytup,'extras':extras}
        else:
            return {'keytup':keytup,'extras':extras,'message':'invalid bbl'}
        """

    def get_lookup_by_rawaddr(self,rawaddr):
        log.debug(":: rawaddr = '%s'" % rawaddr)
        keytup = self.resolve_address(rawaddr)
        log.debug(":: keytup = '%s'" % keytup)
        if keytup is None:
            return {"error":"invalid address (no response from geoclient)"}
        bbl = keytup.get('bbl')
        if bbl is not None:
            if 'message' in keytup:
                # If we get an error message at this stage, it's interepreted as a warning
                # Which we hide from the frontend client (else it will think it's an error condition)
                log.warn(":: bbl=%s, message=[%s]" % (bbl,keytup['message']))
            taxlot = self.dataclient.get_taxlot(bbl)
            if taxlot is None:
                # This is actually a weird condition: the Geoclient gave us a BBL, but none of 
                # our databases recognize it.  Should perhaps handle more forcefully.
                return {"keytup":keytup,"error":"bbl not recognized"}
            else:
                return {"keytup":keytup,"taxlot":taxlot}
        elif 'message' in keytup:
            return {'keytup':keytup,"error":keytup['message']}
        else:
            return {"keytup":keytup,"error":"malformed response from client"}
            # message = "weirdness! geoclient provides invalid BBL '%s'" % keytup['bbl']
            # return {'keytup':keytup,'extras':extras,'message':message}

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
                return { "error":"invalid bbl" }
        else:
            return self.get_lookup_by_rawaddr(query)

    def get_contacts(self,bbl):
        contacts = self.dataclient.get_contacts(bbl)
        return {"contacts":contacts}




# DEPRECATED 
def fix_bin(r):
    """Fixes the keytup's BIN (if null-ish), in-place."""
    log.debug(":: keytup (before) = %s" % r)
    if r['bin'] in nullish:
        r['bin'] = None
    log.debug(":: keytup (after) = %s" % r)

def make_tiny(r):
    tiny = {
        'bbl': softint(r.get('bbl')),
        'bin': softint(r.get('buildingIdentificationNumber')),
    }
    if 'message' in r:
        tiny['message'] = r['message']
    return tiny

# DEPRECATED 
def __make_tiny(r):
    """Extracts just the fields we need from a Geoclient response, and renames
    some of them for the final outgoing message blurb."""
    tiny = _make_tiny(r)
    fix_bin(tiny)
    return tiny


def softint(s):
    return int(s) if s is not None else None


