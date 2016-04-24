import re
from collections import namedtuple

NYCGeoAddress = namedtuple('NYCGeoAddress',['houseNumber','street','borough'])

# Some simple address splitting functions.
#
# Since at present we rely on Google Autocomplete to pre-normalize 
# addreses for us in the search form, we don't need to make thse
# functions too flexible for the time being. 

# Expects an address of the form:
#
#   "43 Mercer Street, Manhattan" 
#
# And if parseable, returns a dict of the form:
#
#   { "street_name":"Mercer Street", "house_number":"43", "boro_name":"Manhattan" }
#
# or None if not parseable. 
pat = {}
pat['street_addr'] = re.compile('^(\S+)\s+(.*)$');
def split_address(rawaddr):
    terms = split_csv(rawaddr)
    if len(terms) != 2:
        return None
    street_address,boro_name = tuple(terms)
    t = split_street_address(street_address)
    if t is None:
        return None
    house_number,street_name = t
    # return house_number,street_name,boro_name
    return NYCGeoAddress(house_number,street_name,boro_name)

def _tuple2param(address_tuple):
    house_number,street_name,boro_name = address_tuple
    return {
        "houseNumber":house_number,
        "street":street_name,
        "borough":boro_name
    }

def address2param(rawaddr):
    address_tuple = split_address(rawaddr)
    if address_tuple is None:
        return None
    return _tuple2param(address_tuple)
    

# '43 Mercer Street' -> (43,'Mercer Street')
def split_street_address(street_addr):
    m = re.match(pat['street_addr'],street_addr)
    if m:
        (house_number,street_name) = m.groups()
        return (house_number,street_name)
    else:
        return None

def split_csv(s):
    return [t.strip() for t in s.split(',')]



