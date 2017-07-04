

"""
A magical function which recursively compares two nested structs,
assuming a "left join" wherever it sees a dict (that is, it only checks
values on the right if the key is also present in the left).

XXX probably slow, and doesn't check for cycles!
"""
def compare(got,exp):
    if got is None and exp is None:
        return True
    if got is None or exp is None:
        return False
    if both_dict(got,exp):
        return compare_dict(got,exp)
    elif both_list(got,exp):
        return compare_list(got,exp)
    elif both_scalar(got,exp):
        return got == exp
    else:
        return False

def compare_dict(got,exp):
    if not both_dict(got,exp):
        return False
    for k in sorted(exp.keys()):
        if k not in got:
            return False
        else:
            return compare(got[k],exp[k])
    return True

def compare_list(got,exp):
    if not both_list(got,exp):
        return False
    if len(got) != len(exp):
        return False
    for a,b in zip(got,exp):
        if not compare(a,b):
            return False
    return True

def both_scalar(x,y):
    return is_scalar(x) and is_scalar(y)

def both_dict(x,y):
    return isinstance(x,dict) and isinstance(y,dict)

def both_list(x,y):
    return isinstance(x,list) and isinstance(y,list)

def is_scalar(x):
    return x is None \
        or isinstance(x,int) \
        or isinstance(x,str) \
        or isinstance(x,bool) \
        or isinstance(x,float) \
        or isinstance(x,bytes);


