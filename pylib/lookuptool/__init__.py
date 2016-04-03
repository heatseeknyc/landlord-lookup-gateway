from .hybrid.factory import instance
#
# A convenience method for applications (so they don't have to know 
# where to find the factory module, above). 
#
def get_lookup_agent(**kwargs):
    return instance(**kwargs)

