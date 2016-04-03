#
# A simplified mock of the NYC Geoclient API, but running off of 
# the HPD registrations table and emitting a much smaller payload. 
#
import simplejson as json
from nychpd.utils import slurp_json
from nychpd.agent import GeoAgent
from flask import Flask, url_for, request, jsonify
from flask.ext.cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

pgconf = slurp_json("config/postgres.json")
agent = GeoAgent(**pgconf)

def errmsg(message):
    return json.dumps({'error':message})

#
# A minimalist endpoint handler which simply calls the internal API,
# catching any exceptions triggered (ensuring that a valid JSON struct 
# is always returned, no matter what we hit it with).
#
@app.route('/geoclient/address.json')
@cross_origin()
def api_lookup():
    r = dict(request.args)
    try:
        resp = agent.get_bbl(r)
    except Exception as e:
        return errmsg('internal error')
    return json.dumps(resp)


# This switch is for testing purposes only, so you can run the 
# service under the default Flask environment (that is, if you 
# invoke this module as a script from the shell enviroment).
#
# Hence, the branch doesn't get entered under WSGI (and the 
# port number below has nothing to do with where the service 
# runs under WSGI).
#
if __name__ == '__main__':
    app.run(port=5003)

