import simplejson as json

def slurp_json(filename):
    with open(filename,"r") as f:
        lines = f.read()
        return json.loads(lines)


