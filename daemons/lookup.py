#!/usr/bin/env python
import simplejson as json
from flask import Flask, url_for, request, jsonify
from flask.ext.cors import CORS, cross_origin
from lookuptool import get_lookup_agent
from lookuptool.utils import slurp_json
from lookuptool.geoutils import city2boro_name 
from traceback import print_tb

app = Flask(__name__)
CORS(app)

dataconf = slurp_json("config/postgres.json")
geoconf  = slurp_json("config/nycgeo.json")
agent = get_lookup_agent(dataconf=dataconf,geoconf=geoconf,mock=False) 

def errmsg(message):
    return json.dumps({'error':message})

def resolve(callf,rawarg):
    try:
        bbl = int(rawarg)
    except ValueError as e:
        return errmsg('invalid argument')
    try:
        print(":: invoke ..")
        recs = callf(bbl)
        print(":: got %d recs." % len(recs))
    except Exception as e:
        print(":: badness = %s" % e)
        return errmsg('internal error')
    print(":: return %d recs." % len(recs))
    return json.dumps(recs)



@app.route('/contacts/<bbl_arg>')
@cross_origin()
def api_contacts(bbl_arg):
    return resolve(lambda bbl:agent.get_contacts(bbl),bbl_arg)

@app.route('/buildings/<bbl_arg>')
@cross_origin()
def api_buildings(bbl_arg):
    return resolve(lambda bbl:agent.get_buildings(bbl),bbl_arg)

@app.route('/lookup/q')
@cross_origin()
def api_lookup():
    r = dict(request.args)
    print("r = ",r)
    try:
        q = normalize_query(r)
        print(":: q = %s" % q)
        resp = agent.get_combined_summary(q)
    except Exception as e:
        print(e)
        print_tb(e.__traceback__)
        return errmsg('internal error')
    return json.dumps(resp)


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
    app.run(port=5002)

