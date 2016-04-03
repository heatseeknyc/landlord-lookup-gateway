import simplejson as json
from nychpd.utils import slurp_json
from nychpd.agent import LookupAgent
from flask import Flask, url_for, request, jsonify
from flask.ext.cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

pgconf = slurp_json("config/postgres.json")
agent = LookupAgent(**pgconf)

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
    # return jsonify(recs)
    return json.dumps(recs)



# This is the only accessor you'll need for 98%+ of all use cases.
@app.route('/lookup/<bbl_arg>')
@cross_origin()
def api_lookup(bbl_arg):
    return resolve(lambda bbl:agent.get_lookup(bbl),bbl_arg)

# These next two are needed only for large-ish rowset responses.
@app.route('/contacts/<bbl_arg>')
@cross_origin()
def api_contacts(bbl_arg):
    return resolve(lambda bbl:agent.get_contacts(bbl),bbl_arg)

@app.route('/buildings/<bbl_arg>')
@cross_origin()
def api_buildings(bbl_arg):
    return resolve(lambda bbl:agent.get_buildings(bbl),bbl_arg)

# Not used by the frontend client, but useful for testing (and is the 
# simplest way to ping the database, see if a BBL is present, and if so,
# what are the sizes of the rowses that will be fetched).
@app.route('/summary/<bbl_arg>')
@cross_origin()
def api_summary(bbl_arg):
    return resolve(lambda bbl:agent.get_summary(bbl),bbl_arg)



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

