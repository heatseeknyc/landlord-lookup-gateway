"""
An ugly, but effective "hybrid agent" that pulls from both the
NYC Geoclient API, and our local database, and smooshes everything
together.
"""
import re
from nycprop.identity import is_degenerate_bbl, is_valid_bbl, is_valid_bin
from gateway.util.address import fix_borough_name
from gateway.util.decorators import wrapsafe
from common.logging import log


class LookupAgent(object):

    def __init__(self,dataclient,geoclient):
        self.dataclient = dataclient
        self.geoclient  = geoclient

    @wrapsafe(log)
    def dispatch(self,endpoint,*args):
        """The preferred entry point to our endpoints."""
        # Yes, there's a bit of repetition here.  
        # We'll be addressing it shortly.
        if endpoint == 'lookup':
            return self.get_lookup(*args)
        if endpoint == 'buildings':
            return self.get_buildings(*args)
        if endpoint == 'contacts':
            return self.get_contacts(*args)
        return {'error':'invalid endpoint'}

    def get_lookup(self,query):
        """Combined geoclient + taxlot summary for an address or a BBL"""
        log.debug(":: query = '%s', type=%s" % (query,type(query)))
        if query is None:
            # This can never happen if we've been properly routed (no matter what 
            # the user types, or the client sends).  But if it does we should treat 
            # it gracefully.
            raise ValueError("invalid usage - null query object")
        q = query.replace('+',' ').strip()
        log.debug("query(stripped) = %s" % str(q))
        if _intlike(query):
            # If our query is integer-like, it means we've either come in via
            # a /taxlot/ URL, or the user has typed in a BBL in the search bar.
            bbl = int(query)
            return self.get_lookup_by_bbl(bbl)
        else:
            # If not then they're at least attempting to provide a valid address.
            return self.get_lookup_by_rawaddr(query)


    def resolve_address(self,rawaddr):
        log.info(":: rawaddr  = '%s'" % rawaddr)
        normaddr = fix_borough_name(rawaddr)
        log.debug(":: normaddr = '%s'" % normaddr)
        status,keytup = self.geoclient.fetch_tiny(normaddr)
        log.debug(":: status = %s " % status)
        log.debug(":: response = %s" % keytup)
        return status,keytup

    #
    # Note that the next two handlers are nearly congruent (once we decide what
    # our BBL is), but have subtly different error handling.
    #


    def get_lookup_by_bbl(self,bbl):
        """
        The primary resolution for all '/lookup/' calls - whether by address or
        BBL, they all go through here.  So in particular, the :bbl argument can be
        either user-supplied, or it can come from the Geoclient (via a call from
        'get_lookup_by_addr', below).  So when interpreting the various switches
        for error chacking and so forth below, keep that in mind.
        """
        log.debug(":: bbl = %s" % bbl)
        keytup = {'bbl':bbl,'bin':None}

        # Carefully distinguish junk BBL cases.
        if not is_valid_bbl(bbl):
            return {'keytup':keytup,'error':'invalid bbl (out of range)'}
        if is_degenerate_bbl(bbl):
            return {'keytup':keytup,'error':'invalid bbl (degenerate)'}

        taxlot = self.dataclient.get_taxlot(bbl)
        if taxlot is None:
            """
            This case should in theory never happen if we're coming in via the
            Geoclient - it would meant that it gave us a BBL that its own databases
            (PAD/Pluto, presumably) fail to recognize.  So if we've gotten here,
            much more likely it's from a user inputting a BBL directly.

            Either way we have nothing to display, and need to bail gracefully.
            """
            return {'keytup':keytup,'error':'bbl not recognized'}
        else:
            """
            If we get here, we're good to go.  There's just one last thing:
            if this is a condo unit, we want to slide in a minified pluto rec
            corresponding to the building (or project)'s baselot.  The does
            involve another database fetch, but the overhead should be minimal.
            """
            if is_condo_unit(taxlot):
                self.attach_baselot(taxlot)
            return {'keytup':keytup,'taxlot':taxlot}

    def get_lookup_by_rawaddr(self,rawaddr):
        log.debug(":: rawaddr = '%s'" % rawaddr)
        status,keytup = self.resolve_address(rawaddr)
        log.debug(":: status = %s" % status)
        code = status.get('code')

        # If we have no response code, it means our input was so bad that we
        # didn't even attempt to conctact the geoclient.
        if code is None:
            return {'error':'malformed address'}

        # This shouldn't happen very often; if it does, that's kind of bad.
        # All the user can do is try again!
        if code != 200:
            return {'error':'no response from geoclient'}

        # Geoclient returned something, but had no 'address' member. 
        # So basically it's barfing at us.  We kind of doubt ths will ever happen,
        # but if it does we should convey what happened.
        if keytup is None:
            return {'error':'malformed response from geoclient'}

        bbl = keytup.get('bbl')
        if 'message' in keytup:
            log.warn(":: weird resolution on bbl=%s, message=[%s]" % (bbl,keytup['message']))

        # If we get here then we still might have a valid address, but if not,
        # at least the Geoclient will provide some explanation for us.
        if bbl is None:
            message = keytup.get('message')
            if message is None:
                message = "[malformed response from Geoclient]"
            error = "cannot resolve address"
            return {'error':error,'message':message}

        # to the lookup-by-bbl case.
        return self.get_lookup_by_bbl(bbl)

    # We used to act on BBL-BIN pairs, but that's been temporarily disabled.
    # For the time being we only act on single BBL arguments.
    def get_contacts(self,keyarg):
        keytup = split_keyarg(keyarg)
        if keytup is None:
            return {'error':'invalid query'}
        _bbl,_bin = keytup
        if _bin is None:
            return {'error':'invalid query (accepts BBL only)'}
        contacts = self.dataclient.get_contacts(_bbl)
        return {"contacts":contacts}

    def get_buildings(self,keyarg):
        keytup = split_keyarg(keyarg)
        if keytup is None:
            return {'error':'invalid query'}
        _bbl,_bin = keytup
        if not is_valid_bbl(_bbl):
            return {'error':'invalid bbl'}
        if _bin is not None and not is_valid_bin(_bin):
            return {'error':'invalid bin'}
        buildings = self.dataclient.get_buildings(_bbl,_bin)
        return {'buildings':buildings}

    #
    # A supporting accessor, not meant to be called as an endpoint.
    #

    def attach_baselot(self,taxlot):
        """Assuming the given taxlot represents a condo unit, mangles that struct
        by attaching a new member, 'baselot', presenting a somewhat minified 'pluto'
        struct for the unit's parent condo lot.  We attach it to the 'condo' member
        struct of the :taxlot struct, which is presumed to already exist."""
        if not is_condo_unit(taxlot):
            return
        condo = taxlot['condo']
        baselot = self.dataclient.get_baselot(condo['parent'])
        if baselot:
            condo['baselot'] = baselot


#
# Support functions
#

def is_condo_unit(taxlot):
    """Tells us whether this taxlot struct represents a condo unit.""" 
    condo = taxlot.get('condo')
    if not condo:
        return False
    parent = condo.get('parent')
    return parent is not None

_keypat = re.compile('(\d+)(,(\d+))?$')
def split_keyarg(keyarg):
    """
    Takes an arbitrary string expected to be of the so-called 'keyarg'
    format, that is, either a single BBL, or a tuple of (BBL,BIN).
    Returns either a 2-tuple (where the first element is always a BBL,
    and the second element either a BIN or None) if the string can be
    thus parsed, or None if it can't be.
    """
    if keyarg is None:
        raise ValueError('invalid usage')
    m = re.match(_keypat,query)
    if m:
        _bbl,_bin = m.group(1),m.group(3)
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


