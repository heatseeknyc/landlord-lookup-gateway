"""
An ugly, but effective "hybrid agent" that pulls from both the
NYC Geoclient API, and our local database, and smooshes everything
together.
"""
from lookuptool.utils.address import fix_borough_name
from common.logging import log

nullish = set([1000000,2000000,3000000,4000000,5000000])

class LookupAgent(object):

    def __init__(self,dataclient,geoclient):
        self.dataclient = dataclient
        self.geoclient  = geoclient

    def get_lookup(self,rawaddr):
        ''' Combined geoclient + ownership summary for a given address'''
        log.info(":: rawaddr  = '%s'" % rawaddr)
        normaddr = fix_borough_name(rawaddr)
        log.debug(":: normaddr = '%s'" % normaddr)
        r,status = self.geoclient.fetch_tiny(normaddr)
        log.debug(":: status = %s " % status)
        log.debug(":: response = %s" % r)
        if r is None:
            return {"error":"invalid address (no response)"}
        nycgeo = make_tiny(r)
        log.debug(":: nycgeo (before) = %s" % nycgeo)
        _bbl,_bin = refine_nycgeo(nycgeo)
        if _bbl is not None:
            extras = self.dataclient.get_summary(_bbl,_bin)
            if 'message' in nycgeo:
                log.info(":: WARNING bbl=%s, message=[%s]" % (_bbl,r['message']))
            return {"nycgeo":nycgeo,"extras":extras}
        else:
            if 'message' in nycgeo:
                return {"nycgeo":nycgeo,"extras":None,"error":nycgeo['message']}
            else:
                return {"nycgeo":nycgeo,"extras":extras}

    def get_contacts(self,bbl):
        contacts = self.dataclient.get_contacts(bbl)
        return {"contacts":contacts}



def refine_nycgeo(r):
    """Refines an nycgeo struct, in-place.  Returns the pair (bbl,bin) for convenience."""
    _bbl = r.get('bbl')
    _bin = r.get('bin')
    if _bin in nullish:
        log.info(":: refine'd: bbl = %s, bin = %s => None" % (_bbl,_bin))
        _bin = r['bin'] = None
    else:
        log.info(":: refine'd: bbl = %s, bin = %s" % (_bbl,_bin))
    return _bbl,_bin


# XXX need a better name for this function + better description.
def make_tiny(r):
    """Extracts just the fields we need from a Geoclient response, and renames
    some of them for the final outgoing message blurb."""
    tiny = {
        'bbl': softint(r.get('bbl')),
        'bin': softint(r.get('buildingIdentificationNumber')),
    }
    if 'message' in r:
        tiny['message'] = r['message']
    return tiny

def softint(s):
    return int(s) if s is not None else None


