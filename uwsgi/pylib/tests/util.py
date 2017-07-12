
"""
A magical function which recursively compares two nested structs,
assuming a "left join" wherever it sees a dict (that is, it only checks
values on the right if the key is also present in the left).

XXX probably slow, and doesn't check for cycles!
"""
def compare(got,exp):
    if got is None and exp is None:
        return None
    if got is None or exp is None:
        return []
    if both_dict(got,exp):
        return compare_dict(got,exp)
    elif both_list(got,exp):
        return compare_list(got,exp)
    elif both_scalar(got,exp):
        status = got == exp
        if not status:
            return []
    else:
        return ['--incompat--']

def compare_dict(got,exp):
    if not both_dict(got,exp):
        return False,None
    # print("got.keys = %s" % list(got.keys()))
    # print("exp.keys = %s" % list(exp.keys()))
    for k in sorted(exp.keys()):
        # print("check %s .." % k)
        if k not in got:
            return ['--missing--',k]
        path = compare(got[k],exp[k])
        if path:
            path += [k]
            return path
    return None

def compare_list(got,exp):
    if not both_list(got,exp):
        return ['--incompat--']
    if len(got) != len(exp):
        return ['--badlen--']
    for i,t in enumerate(zip(got,exp)):
        a,b = t
        path = compare(a,b)
        if path:
            path += [i]
            return path
    return None

def both_scalar(x,y):
    return is_scalar(x) and is_scalar(y)

def both_dict(x,y):
    return isinstance(x,dict) and isinstance(y,dict)

def both_list(x,y):
    return isinstance(x,list) and isinstance(y,list)

def is_scalar(x):
    """
    By 'scalar' we mean basically that it's not a dict or a list, and is more like
    a number or a string.  In particular, it should compare with the == operator.
    Works for now but we should perhaps think about this definition more carefully.
    """
    return x is None \
        or isinstance(x,int) \
        or isinstance(x,str) \
        or isinstance(x,bool) \
        or isinstance(x,float) \
        or isinstance(x,bytes);


def displaypath(path):
    status = not bool(path)
    longpath = ".".join(reversed(path)) if path else None
    return status,longpath
