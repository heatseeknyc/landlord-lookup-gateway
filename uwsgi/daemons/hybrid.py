#!/usr/bin/env python
#
# Our actual public-facing REST gateway.  For details as to the 
# endpoints and protocol, please see:
#
#   documentation/ABOUT-rest-protocol.rst
#
# in this repo.
#
import re
import argparse
import simplejson as json
from traceback import print_tb
from flask import Flask
from flask_cors import CORS, cross_origin
import gateway.hybrid
from gateway.util.misc import slurp_json
from daemons.util.decorators import wrapsafe
from common.logging import log

parser = argparse.ArgumentParser()
parser.add_argument('--mock',    dest='mock',   action='store_true')
parser.add_argument('--no-mock', dest='nomock', action='store_true')
parser.add_argument("--port", help="port to listen at", type=int)
args = parser.parse_args()

port = args.port if args.port else 5002
app = Flask(__name__)
CORS(app)

metaconf = slurp_json("config/hybrid-settings.json")
dataconf = slurp_json("config/postgres.json")

#
# Resolution order for the 'mock' flag:
#
#  - if either of the arg flags '--mock' or '--no-mock' are invoked, 
#    go with that.
#
#  - otherwise rely on what the hybrid settings config says.
#

if args.mock:
    usemock = True
elif args.nomock:
    usemock = False
else:
    usemock = metaconf['mock']


if usemock:
    geoconf  = slurp_json("config/nycgeo-mock.json")
else:
    geoconf  = slurp_json("config/nycgeo-live.json")

log.info("mock = %s, port = %d" % (usemock,port))
log.info("siteurl = '%s'" % geoconf.get('siteurl'))
agent = gateway.hybrid.instance(dataconf,geoconf)


#
# There's some obvious repetition in the next 3 method declarations.
# Which could be avoided by adding another decorator.  However, we'd 
# prefer not to go that route for the time being.
#
@app.route('/lookup/<query>')
@cross_origin()
def api_lookup(query):
    r = resolve_lookup(query)
    return jsonify(r)

@app.route('/contacts/<keytup>')
@cross_origin()
def api_contacts(keytup):
    return _wrapsafe(resolve_contacts,keytup)

@app.route('/buildings/<keyarg>')
@cross_origin()
def api_building(keyarg):
    return _wrapsafe(resolve_buildings,keyarg)



@wrapsafe(log)
def resolve_lookup(query):
    """
    Resolves (does some kind of a taxlot summary search on) the given search query,
    that is, the (whitespace-trimmed) search string as supplied on the main search form.
    """
    q = query.replace('+',' ').strip()
    log.debug("q = %s" % str(q))
    if q is None:
        # return errmsg('invalid query string')
        return {'error':'invalid query string'}
    else:
        return agent.get_lookup(q)
        # response = agent.get_lookup(q)
        # return jsonify(response)

def resolve_contacts(keytup):
    t = split_keytup(keytup)
    if t is None:
        return errmsg('invalid argument pair')
    else:
        contacts = agent.dataclient.get_contacts(*t)
        return jsonify({"contacts":contacts})

def resolve_buildings(keyarg):
    # log.info("bbl = [%s]" % bbl)
    # n = parsebbl(bbl)
    #if n is None:
    #    return errmsg('invalid BBL string')
    # else:
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


