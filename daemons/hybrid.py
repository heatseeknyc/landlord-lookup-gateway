#!/usr/bin/env python
import argparse
import simplejson as json
from traceback import print_tb
from flask import Flask, url_for, request, jsonify
from flask.ext.cors import CORS, cross_origin
import lookuptool.hybrid
from lookuptool.utils.misc import slurp_json
from lookuptool.utils.address import city2boro_name 
from nycgeo.utils.url import split_query

parser = argparse.ArgumentParser()
parser.add_argument('--mock', dest='mock', action='store_true')
parser.add_argument('--no-mock', dest='mock', action='store_false')
parser.add_argument("--port", help="port to listen at", type=int)
args = parser.parse_args()

port = args.port if args.port else 5002



app = Flask(__name__)
CORS(app)

dataconf = slurp_json("config/postgres.json")
if args.mock:
    geoconf  = slurp_json("config/mockgeo-client.json")
else:
    geoconf  = slurp_json("config/nycgeo.json")
agent = lookuptool.hybrid.instance(dataconf,geoconf) 

def errmsg(message):
    return json.dumps({'error':message})

def jsonify(r):
    return json.dumps(r,sort_keys=True)

def wrapsafe(callf,rawarg):
    try:
        return callf(rawarg)
    except Exception as e:
        print(e)
        print_tb(e.__traceback__)
        return errmsg('internal error')

def resolve_lookup(address):
    q = address.replace('+',' ').strip()
    print(":: q = %s" % str(q)) 
    if q is None: 
        return errmsg('invalid query string')
    else:
        response = agent.get_lookup(q)
        return jsonify(response)

def resolve_contacts(keytup):
    t = split_keytup(keytup)
    if t is None:
        return errmsg('invalid argument pair')
    else:
        contacts = agent.dataclient.get_contacts(*t)
        return jsonify({"contacts":contacts})

def split_keytup(keytup):
    terms = keytup.split(',')
    if len(terms) == 2:
        return map(int,terms)
    else:
        return None

@app.route('/lookup/<address>')
@cross_origin()
def api_lookup(address):
    return wrapsafe(resolve_lookup,address)

@app.route('/contacts/<keytup>')
@cross_origin()
def api_contacts(keytup):
    return wrapsafe(resolve_contacts,keytup)


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
print (":: listen to %d .." % port)
if __name__ == '__main__':
    app.run(port=port)


