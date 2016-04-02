from collections import defaultdict
from lookuptool.agent.base import AgentBase
from lookuptool.geoutils import normalize_street_name, city2boro


#
# Designed to be interface-compatible with the who.owns.nyc service,
# with some enhancements.  So it will take a URL of the form 
#
#   /geoclient/address.json?borough=3&street=Bushwick+Ave&houseNumber=590
#
# as prescribed by that service; or, it can take a variant form based
# on city name (unique to our service):
#
#   /geoclient/address.json?city=Brooklyn&street=Bushwick+Ave&houseNumber=590
#
# Or a query with no city or borough provided (given that the combination 
# of street_name + house_number is unique for 99% of all NYC addresses):
#
#   /geoclient/address.json?street=Bushwick+Ave&houseNumber=590
#
# and do it's best to pull the BBL from our database, or a nice error 
# message otherwise. Note that by "city name" we mean either a borough name
# or pre-annexation "municipality" that commonly appears in NYC postal 
# addresses, e.g. "Forest Hills".
#
# In both cases, we return a (stripped-down) dict strict intended to be
# ompatible with the nested struct returned by the who.owns service,
# but restricted to just the fields of interest.  For example, for 
# the query string above we'll get the follwing nested struct as a
# response:
#
#     {'address': {'bbl': 3031500031}}
#
# And in failure cases we'll get one of the error message blobs 
# you'll find in the code below.
# 

class MockGeoclient(AgentBase):

    def get_bbl(self,args):
        if args is None:
            return {'address':{'message':'null argdict'}}
        (normal,errmsg) = normalize(args)
        if normal is None:
            return {'address':{'message':errmsg}}
        query = makequery(normal)
        cur = self.dict_cursor()
        cur.execute(query)
        recs = [dict(r) for r in cur.fetchall()]
        if len(recs) == 1:
            return {'address':{'bbl':recs[0]['bbl']}}
        else:
            return diagnose(recs)


# Provide lucid diagnostics for non- or ambiguously-matching rowsets.
def diagnose(recs):
    # The most frequently occuring case - no matches.
    if len(recs) < 1:
        return {'address':{'message':'unknown address'}}
    # Multiple matches are extremely rare, and fall into two basic types:
    elif len(recs) > 1:
       if is_multi_boro(recs):
           # This case should only occur when no borough (or municipality) has 
           # been provided, and we've been given one of about 450 addresses which, 
           # going by the tuple (street_name,house_number) are present in more 
           # than one borough.  Usually these are numbered streets in Manhattan or 
           # Brooklyn, but it happens to a handful of named streets as well.
           # Example: 155 Bleecker St.
           message = "cannot resolve (address has matches within multiple boroughs)"
       else:
           # This case applies to about 17 degenerate (broken) addresses which 
           # have more than one BBL associated (within the raw HPD dataset).
           # Apparently these are "upserts" where the BBL was entered differently 
           # the second time for whatever reason.  Example: 87 Pulaski St.
           message = "cannot resolve (address has multiple matches within a single borough)"
       return {'address':{'message':message}}
    else:
        # This case should never occur; if it does we aren't using this
        # function properly.
        raise ValueError("invalid usage -- not a single-record rowset")


# Whether our result set contains records from multiple boroughs.
def is_multi_boro(recs):
    boros = set(r.get('boro_id') for r in recs)
    return len(boros) > 1

#
# Takes a normalized args dict, returns a SQL query.
# 

# Canonical use case, with all 3 fields present.
# The boro_id field is redundant in this case, but we 
# pull it anyway to be structurally compatible with the
# "partial" query, below.
query_full = """
select bbl, boro_id from hard.registrations where
house_number = '%(house_number)s' and
street_name = '%(street_name)s' and
boro_id = '%(boro_id)d'
order by bbl
"""

# If no boro_id is presented, we can attempt to match 
# on house number and street name alone.  
query_partial = """
select bbl, boro_id from hard.registrations where
house_number = '%(house_number)s' and
street_name = '%(street_name)s'
order by bbl
"""

# Takes a normalized argdict (as returned by 'normalize'), and returns 
# a fully mapped SQL query.  Since we assume our input struct to be fully 
# normalized, we don't do any error checking at this stage.  If an invalid 
# (non-formattable) struct does slip through, an appropriate exception 
# will be raised by the % operator.
def makequery(t):
    if 'boro_id' in t:
        return query_full % t 
    else:
        return query_partial % t


#
# A simple idiom which tells us whether a dict has a given key, 
# and if so, whether the args[k] is a string of non-zero length.   
#
def haskey(args,k):
    return k in args and args[k] is not None and len(args[k])

#
# Takes a query dict, and attempts to map it into a struct of 
# normalized database fields that can be slotted into a SQL query, 
# or diagnostic string if the dict can't be mapped.
#
# In either case, we always return a tuple of (normal,errmsg); exactly
# one of these will be present -- and we'll return a normalized struct
# only if the input dict can be fully mapped. 
#
# XXX More lucid validation + basic SQL injection defense needed.
#
def normalize(arglist):
    args = dictify(arglist)
    normal = {}
    for k in ('houseNumber','street'):
        if k not in args:  
            errmsg = "at least a house number and a street name must be present";
            return (None,errmsg)
    normal['house_number'] = args['houseNumber']
    normal['street_name'] = normalize_street_name(args['street'])
    if haskey(args,'borough'):
        normal['boro_id'] = int(args['borough'])
    if haskey(args,'city'):
        boro_id = city2boro(args['city'])
        if boro_id in (1,2,3,4,5): 
            normal['boro_id'] = boro_id 
        elif boro_id == 'any':
            # The 'any' tag means we've been given a borough/city name like 
            # "New York", which we take to mean "unspecified", that is, the
            # same as if no name were given at all.
            pass 
        else:
            # If we get here it means we've been given a non-NYC city name. 
            return (None,"unknown municipality")
    return (normal,None) 

#
# Skrunches arg hashes to a more wieldy {key:val} form instead
# of the {key:[list-of-vals] form that they come in (to represent
# degeneate query strings with multiple occurrences of the same
# parameter term), 'foo=bar&foo=ook'.
#
# Our approach is to simply ignore all subsequent occurrences of 
# a given named parameter.  
#
def dictify(args):
    return {k:v[0] for k,v in sorted(args.items())}


#
# A simple query string splitter, for use in testing environments.
# Takes a query string of the form:
#
#   'borough=3&street=Bushwick+Ave&houseNumber=590' 
#
# and returns the appropriate dict.
#

def split_kv(term):
    kv = term.split('=')
    if len(kv) == 1:
        return (kv[0],'')
    if len(kv) == 2:
        return tuple(kv)
    raise ValueError("bad term ['%s'] in query string" % term)

def _decode(s):
    return s.replace('+',' ')

def decode_pairs(pairs):
    return [ (_decode(k),_decode(v)) for k,v in pairs ]

# XXX optimize dict
def split_query(s):
    r = defaultdict(list)
    terms = s.split('&')
    pairs = [split_kv(t) for t in terms]
    pairs = decode_pairs(pairs)
    for k,v in pairs:
        r[k].append(v)
    return dict(r)

