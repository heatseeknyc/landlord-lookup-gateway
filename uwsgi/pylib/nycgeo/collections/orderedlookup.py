from copy import deepcopy

#
# A simple hybrid list/dict lookup structure which, unlike an OrderedDict,
# also provides positional key access, albeit at the cost of a somewhat impure
# interface.  But that's OK because we just need it for the simple purpose
# of storing records that can be accessed both sequentially and via key lookup.
#
# There are some addition tweeks to make record access somewhat safer in
# testing environments (like the fact that we deepcopy our lookup values on 
# the way out, to keep our mock data immutable-ish).
#
class OrderedLookup(object):

    def __init__(self,pairs):
        self.consume(pairs)

    def consume(self,pairs):
        self._keys = []
        self._look = {} 
        for k,v in pairs:
            self._keys.append(k)
            self._look[k] = deepcopy(v)

    def get(self,k):
        return deepcopy(self._look.get(k))

    def keys(self):
        return (k for k in self._keys)

    def items(self):
        return ((k,self.get(k)) for k in self.keys())

    def __len__(self):
        return len(self._keys)

    def __getitem__(self,i):
        return self._keys[i]

    def __iter__(self):
        return self.keys()

    def __contains__(self,k):
        return k in self._look


