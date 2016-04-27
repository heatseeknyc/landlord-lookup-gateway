import re
from copy import deepcopy
from nycgeo.utils.address import split_address

#
# Municipality => Borough mapping.
#
# Whereby we attempt to map the "city" part of an address to one of 
# NYC's 5 borough codes 1-5.
#
# This would be a trivial task, were it not for the magic of Google
# Autocomplete - which for some reason likes to supply "village" or former 
# municipality names for Queens address (and never simply "Queens").
#
# It also likes to do so quite erratically (you'll find it offering
# many choices of "municipality" for a given street address).
#
# Fortunately all we care about is the borough designation, so it suffices
# to simply map all of these village names to id = 4, and be done with it.
#
# This approach has some built-in bugs: since we don't check for alignment 
# on state prefix, it's quite possible one could type in part of an address
# in Oakland, CA (or various other matching city names throughout the U.S.)
# and have our service respond as if it's an NYC address.  But I suppose 
# we can fix that later.
#


# Pre-annexation municipalities in the wonderful borough of Queens. 
# These were grabbed from some random site somewhere, so many not overlap 
# exactly with the set of names that Google uses -- but it would seem to 
# be a reasonable place to start.

# Present names as cased, for readiblity. 
queens_municipalities = [
  'Arverne', 'Astoria', 'Bay Terrace', 'Bayside', 'Beechhurst', 
  'Bellerose', 'Borough Hall', 'Breezy Point', 'Briarwood', 'Broad Channel', 
  'Cambria Heights', 'College Point', 'Corona', 'Douglaston', 'East Elmhurst', 
  'Edgemere', 'Elmhurst', 'Far Rockaway', 'Floral Park', 'Flushing', 
  'Forest Hills', 'Fort Tilden', 'Fort Totten', 'Fresh Meadows', 'Fresh Pond', 
  'Glen Oaks', 'Glendale', 'Hollis', 'Howard Beach', 'Jackson Heights', 
  'Jamaica', 'Jamaica Estates', 'John F Kennedy Airport', 'Kew Garden Hills', 
  'Kew Gardens', 'La Guardia Airport', 'Laurelton', 'Linden Hill', 
  'Little Neck', 'Long Island City', 'Malba', 'Maspeth', 'Middle Village', 
  'Neponsit', 'Oakland Gardens', 'Ozone Park', 'Parkside', 'Pomonok', 
  'Queens Village', 'Rego Park', 'Richmond Hill', 'Ridgewood', 'Rochdale', 
  'Rochdale Village', 'Rockaway Beach', 'Rockaway Park', 'Rockaway Point', 
  'Rosedale', 'Saint Albans', 'South Ozone Park', 'South Richmond Hill', 
  'Springfield Gardens', 'Sunnyside', 'Trainsmeadow', 'Utopia', 'Wave Crest', 
  'Whitestone'
]
queens_upper = set(q.upper() for q in queens_municipalities) 

def munge_queens_name(s):
    return "Queens" if s.upper() in queens_upper else s

def fix_queens_name(rawaddr):
    param = split_address(rawaddr)
    if param:
        canon_borough = munge_queens_name(param.borough)
        return "%s %s, %s" % (param.houseNumber, param.street, canon_borough) 
    else:
        return rawaddress



#
# Deprecated STuff
#


classic = {'Manhattan':1,'Bronx':2,'Brooklyn':3,'Queens':4,'Staten Island':5}


# Now let's smooch everything together, upper-casing along the way 
boro2id = {k.upper():v for k,v in classic.items()}
boro2id.update({k.upper():4 for k in queens_municipalities})
boro2id.update({k.upper():'any' for k in ['New York','New York City','NYC']})

# Returns (if given):
#   1-5   - something that uniquely identifies a borough;
#   'any' - something like "New York" or "New York City"
#   None  - something which doesn't look like it indicates NYC. 
def city2boro_id(city):
    return boro2id.get(city.upper())

id2name = {classic[k]:k for k in classic.keys()}
def city2boro_name(city):
    boro_id = city2boro_id(city)
    if boro_id is not None:
        return id2name[boro_id]
    else:
        return None



# A quick-and-dirty street normalization algorithm.
#
# Basically it aims to replicate the same logic as used in the cleanup 
# stage for property addresses via 'fix-registration-contacts.sql', but 
# with some gaps (we omit a few steps from that script we don't quite 
# understand).
#
# The bigger flaw is that it's a huge DRY violation to have this logic
# replicated in two different places.  We're aware of that, but it's all 
# good, because again this just a throwaway step in what will probably 
# be a throwaway service anyway.
#
# Some more minor flaws:
#
#   - We don't attempt any normalization on "Queens" addresses
#   (house numbers with embedded dashes, which in rare cases occur
#   in other boroughs, also). Generally these are present in the
#   database in "dashed" form; so if a non-dashed form is given, 
#   it will fail to match.
#
# Beyond that we won't describe the logic in detail because we hope
# that it's more or less self-documenting.  
normal_suffix = {
    'AVE':'AVENUE',
    'ST' :'STREET',
    'STR':'STREET',
    'LA' :'LANE',
    'LN' :'LANE',
    'PL' :'PLACE',
    'RD' :'ROAD',
    'PKWY' :'PARKWAY',
    'BLVD' :'BOULEVARD',
    'BCH' :'BEACH',
}
normal_prefix = {
    'E':'EAST', 
    'W':'WEST', 
    'N':'NORTH', 
    'S':'SOUTH', 
}
def normalize_street_name(s):
    s = s.strip().upper()
    s = re.sub('\.','',s)
    t = s.split(' ')
    if len(t) <= 1: return s
    if t[-1] in normal_suffix: t[-1] = normal_suffix[t[-1]] 
    if t[0]  in normal_prefix: t[0]  = normal_prefix[t[0]] 
    s = ' '.join(t)
    s = re.sub('(\d+)(?:TH|RD|ND|ST)', lambda m:m.group(1), s)
    return s 


