import re

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
  'Neponsit', 'Oakland', 'Gardens', 'Ozone Park', 'Parkside', 'Pomonok', 
  'Queens Village', 'Rego Park', 'Richmond Hill', 'Ridgewood', 'Rochdale', 
  'Rochdale Village', 'Rockaway Beach', 'Rockaway Park', 'Rockaway Point', 
  'Rosedale', 'Saint Albans', 'South Ozone Park', 'South Richmond Hill', 
  'Springfield Gardens', 'Sunnyside', 'Trainsmeadow', 'Utopia', 'Wave Crest', 
  'Whitestone'
]

# Now let's smooch everything together.  
# Present city names as cased, for readiblity. 
boro = {'Manhattan':1,'Bronx':2,'Brooklyn':3,'Queens':4,'Staten Island':5}
boro.update({k:4 for k in queens_municipalities})
boro.update({k:'any' for k in ['New York','New York City','NYC']})
# Then convert to upper case in the final dict.
boro = {k.upper():v for k,v in boro.items()}

# Returns (if given):
#   1-5   - something that uniquely identifies a borough;
#   'any' - something like "New York" or "New York City"
#   None  - something which doesn't look like it indicates NYC. 
def city2boro(city):
    return boro.get(city.upper())

#
# Address normalization
#

pat = {}
pat['terms'] = re.compile('^\s*(.*?)\s*,\s*(.*?)\s*,\s*(.*?)\s*$') 
pat['street_addr'] = re.compile('^(\d+)\s+(.*)$');
pat['state_and_zip'] = re.compile('^(\S+)\s+(\d+)$');

#
# Takes a string of the form:
#
#    '43 Mercer Street, New York, NY 10013'
#
# If it's a reasonably valid address, returns a dict of the form:
#
#   {'house_number':'43', 'street_name':'Mercer Street', 'zipcode':'10013'}
#
# Optional 'upper' argument forces street_name to upper case.
#
def split_address(raw,upper=False):
    m = re.match(pat['terms'],raw)
    if m:
        (street_addr,city,state_and_zip) = m.groups() 
        t = _split_street_address(street_addr)
        if t is None: return None
        (house_number,street_name) = t 
        t = _split_state_and_zip(state_and_zip)
        if t is None: return None
        (state,zipcode) = t
        if upper: street_name = street_name.upper()
        return {
            'house_number': house_number,
            'street_name':street_name,
            'zipcode':zipcode
        }        
    else:
        return None


# 'NY 10013' -> ('NY','10013')
def _split_state_and_zip(state_and_zip):
    m = re.match(pat['state_and_zip'],state_and_zip)
    if m:
        (state,zipcode) = m.groups()
        return (state,zipcode)
    else:
        return None


# '43 Mercer Street' -> (43,'Mercer Street')
def _split_street_address(street_addr):
    m = re.match(pat['street_addr'],street_addr)
    if m:
        (house_number,street_name) = m.groups()
        return (house_number,street_name)
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
    # print(":: name = ",s)
    s = s.strip().upper()
    s = re.sub('\.','',s)
    t = s.split(' ')
    if len(t) <= 1: return s
    if t[-1] in normal_suffix: t[-1] = normal_suffix[t[-1]] 
    if t[0]  in normal_prefix: t[0]  = normal_prefix[t[0]] 
    s = ' '.join(t)
    s = re.sub('(\d+)(?:TH|RD|ND|ST)', lambda m:m.group(1), s)
    return s 

# '(.*)(\d+)(?:TH|RD|ND|ST)( .+)'), '') WHERE streetname ~ '.*(\d+)(?:TH|RD|ND|ST)( .+).*';
# UPDATE flat.registrations SET streetname = regexp_replace( streetname, '\.', '', 'g');

