import re
from collections import namedtuple

#
# Our preferred container for parsed addresses.  The field names 
# are exactly those used by the Geoclient API.
#
NYCGeoAddress = namedtuple('NYCGeoAddress',['houseNumber','street','borough'])





#
# Since at present we rely on Google Autocomplete to pre-normalize 
# addreses for us in the search form, we don't need to make thse
# functions too flexible for the time being. 
#

# Expects an address of the form:
#
#   "43 Mercer Street, Manhattan" 
#
# And if parseable, returns a named tuple of the form: 
#
#   NYCGeoAddress(houseNumber='43',street='Mercer Street',borough='Manhattan')
#
# or None if not parseable.  Note that only the first 2 comma-separated terms 
# are considered; so the raw address 
#
#   '285 Lafayette Street, New York, NY, United States' =>
#
# will be treated as equivalent to:
#
#   '285 Lafayette Street, New York'
#
pat = {}
pat['street_addr'] = re.compile('^(\S+)\s+(.*)$');
def split_address(rawaddr):
    terms = split_csv(rawaddr)
    if len(terms) < 2:
        return None
    street_address,boro_name = terms[0:2]
    t = split_street_address(street_address)
    if t is None:
        return None
    house_number,street_name = t
    # return house_number,street_name,boro_name
    return NYCGeoAddress(house_number,street_name,boro_name)

def split_csv(s):
    return [t.strip() for t in s.split(',')]

# '43 Mercer Street' -> (43,'Mercer Street')
def split_street_address(street_addr):
    m = re.match(pat['street_addr'],street_addr)
    if m:
        (house_number,street_name) = m.groups()
        return (house_number,street_name)
    else:
        return None


