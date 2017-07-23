#
# Our actual public-facing REST gateway, as such.
# Currently provides 3 endpoints:
#
#      /lookup/
#      /buildings/
#      /contacts/
#
# We'll get around to documenting them, at some point.
# But they're really quite simple.
#
import re
import argparse
import simplejson as json
from traceback import print_tb
from flask import Flask
from flask_cors import CORS, cross_origin
import gateway.hybrid
from daemons.util.config import load_hybrid_conf
from common.logging import log

parser = argparse.ArgumentParser()
parser.add_argument('--mock',    dest='mock',   action='store_true')
parser.add_argument('--no-mock', dest='nomock', action='store_true')
parser.add_argument("--port", type=int, default=5002, help="port to listen at")
args = parser.parse_args()

CONFDIR = 'config'

dataconf,geoconf = load_hybrid_conf(CONFDIR,args)
hybrid = gateway.hybrid.instance(dataconf,geoconf)
app = Flask(__name__)
CORS(app)



#
# There's some obvious repetition in the next 3 method declarations.
# Which could be avoided by adding another decorator.  However, we'd 
# prefer not to go that route for the time being.
#
@app.route('/lookup/<query>')
@cross_origin()
def api_lookup(query):
    r = hybrid.dispatch('lookup',query)
    return jsonify(r)

@app.route('/contacts/<keytup>')
@cross_origin()
def api_contacts(keytup):
    return _wrapsafe(resolve_contacts,keytup)

@app.route('/buildings/<keyarg>')
@cross_origin()
def api_building(keyarg):
    return _wrapsafe(resolve_buildings,keyarg)

def resolve_lookup(agent,query):
    """
    Resolves (does some kind of a taxlot summary search on) the given search query,
    that is, the (whitespace-trimmed) search string as supplied on the main search form.
    """
    q = query.replace('+',' ').strip()
    log.debug("q = %s" % str(q))
    if q is None:
        return {'error':'invalid query string'}
    else:
        return agent.get_lookup(q)

def resolve_contacts(keytup):
    t = split_keytup(keytup)
    if t is None:
        return errmsg('invalid argument pair')
    else:
        contacts = agent.dataclient.get_contacts(*t)
        return jsonify({"contacts":contacts})

def resolve_buildings(keyarg):
    log.debug("keyarg = [%s]" % keyarg)
    r = agent.get_buildings(keyarg)
    return jsonify(r)

def _wrapsafe(callf,rawarg):
    try:
        return callf(rawarg)
    except Exception as e:
        log.info("exception = %s" % e)
        log.exception(e)
        return errmsg('internal error')

def errmsg(message):
    return json.dumps({'error':message})

def jsonify(r):
    return json.dumps(r,sort_keys=True)

#
# Helper functions
#

def split_keytup(keytup):
    terms = keytup.split(',')
    if len(terms) == 2:
        return map(int,terms)
    else:
        return None

_bblpat = re.compile('^\d{10}$')
def parsebbl(s):
    return int(s) if re.match(_bblpat,s) else None

#
# This switch is for testing purposes only, so you can run the 
# service under the default Flask environment (that is, if you 
# invoke this module as a script from the shell enviroment).
#
# Hence, the branch doesn't get entered under WSGI (and the 
# port number below has nothing to do with where the service 
# runs under WSGI).
#
if __name__ == '__main__':
    app.run(port=port)


