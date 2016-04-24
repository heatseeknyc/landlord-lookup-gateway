#!/usr/bin/env python
import simplejson as json
from flask import Flask, url_for, request, jsonify
from flask.ext.cors import CORS, cross_origin
from nycgeo.server.agent import GeoServerMockAgent
from nycgeo.utils.url import split_query, split_baseurl
from nycgeo.utils.address import NYCGeoAddress 
from traceback import print_tb

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
    print(":: param = %s" % param) 
    fields = 'houseNumber','street','borough'
    messy = {k:param.get(k) for k in fields}
    clean = {k:mapcgi(messy[k]) for k in messy}
    print(":: clean = %s" % clean) 
    return NYCGeoAddress(**clean)

def resolve_query(query_string):
    param = extract_param(query_string)
    print(":: named = %s" % str(param)) 
    response = agent.lookup(param)
    return jsonmsg(response)

@app.route('/geoclient/v1/<prefix>')
@cross_origin()
def api_fetch(prefix):
    if prefix != 'address.json':
        return errmsg('invalid service base')
    try:
        print(":: query_string = %s" % request.query_string)
        return resolve_query(request.query_string)
    except Exception as e:
        return errmsg('internal error')

@app.route('/echoparam/<prefix>')
@cross_origin()
def api_echoparam(prefix):
    param = split_query(request.query_string.decode('utf-8'))
    return json.dumps({'param':param,'servicebase':prefix})


@app.route('/ping')
@cross_origin()
def api_hello():
    return "Woof!"
        


def resolve(callf,query):
    try:
        param = split_query(query)
    except ValueError as e:
        return errmsg('invalid query string')
    try:
        print(":: invoke ..")
        r = callf(param)
        print(":: got dict with %d keys." % len(r))
    except Exception as e:
        print(":: badness = %s" % e)
        return errmsg('internal error')
    print(":: return dict with %d keys." % len(r))
    return jsonify(r,sort_keys=True)


def normalize_query(r):
    city   = r.pop('city')[-1]
    street = r.pop('street')[-1]
    number = r.pop('number')[-1]
    return {
        'street_name': street, 
        'house_number': number, 
        'boro_name': city2boro_name(city)
    };


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

