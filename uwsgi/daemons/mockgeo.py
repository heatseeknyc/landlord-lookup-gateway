#!/usr/bin/env python
import simplejson as json
from flask import Flask, request
from flask_cors import CORS, cross_origin
from nycgeo.server.agent import GeoServerMockAgent
from nycgeo.utils.url import split_query
from nycgeo.utils.address import NYCGeoAddress
from traceback import print_tb
from common.logging import log

app = Flask(__name__)
CORS(app)

servercfg = json.loads(open("config/mockgeo-server.json","r").read())
mockdata  = json.loads(open("tests/data/mockdata.json","r").read())
mockaddr  = [r['address'] for r in mockdata]

agent = GeoServerMockAgent(mockdata)

def errmsg(message):
    return json.dumps({'error':message})

def jsonify(r):
    return json.dumps(r,sort_keys=True)

def mapcgi(s):
    return None if s is None else s.replace('%20',' ')

def extract_param(query_string):
    param = split_query(query_string.decode('utf-8'))
    log.debug("param = %s" % param)
    fields = 'houseNumber','street','borough'
    messy = {k:param.get(k) for k in fields}
    clean = {k:mapcgi(messy[k]) for k in messy}
    log.debug("clean = %s" % clean)
    return NYCGeoAddress(**clean)

def resolve_query(query_string):
    param = extract_param(query_string)
    log.debug("named = %s" % str(param))
    response = agent.lookup(param)
    log.debug("response = %s" % response)
    return jsonify(response)

#
# Our main endpoint, designed to be drop-in compatible with the endpoing 
# we used in the NYCGeoclient API (except that credentials are ignored; and
# that only a handful of addresses are responded to, which also need to be
# precisely formatted so as to match the data in tests/data/mockdata.json). 
#
@app.route('/geoclient/v1/<prefix>')
@cross_origin()
def api_fetch(prefix):
    if prefix != 'address.json':
        return errmsg('invalid service base')
    try:
        log.debug("query_string = %s" % request.query_string)
        return resolve_query(request.query_string)
    except Exception as e:
        log.info("exception = %s" % e)
        return errmsg('internal error')

#
# A couple of troubleshooting endpoints.
#
@app.route('/echoparam/<prefix>')
@cross_origin()
def api_echoparam(prefix):
    param = split_query(request.query_string.decode('utf-8'))
    return json.dumps({'param':param,'servicebase':prefix})

@app.route('/ping')
@cross_origin()
def api_hello():
    return "Woof!"
 


# Deprecated
def resolve(callf,query):
    try:
        param = split_query(query)
    except ValueError as e:
        return errmsg('invalid query string')
    try:
        r = callf(param)
    except Exception as e:
        log.info("exception = %s" % e)
        return errmsg('internal error')
    return jsonify(r,sort_keys=True)



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
    app.run(port=servercfg['port'])

