import sys, time, argparse
import simplejson as json
from lookuptool.agent import DataClient

parser = argparse.ArgumentParser()
parser.add_argument("--mode", help="what to pull")
parser.add_argument("--key", help="BBL,BIN pair to use as primary key")
args = parser.parse_args()

configpath = "config/postgres.json"
dataconf = json.loads(open(configpath,"r").read())

if args.key:
    _bbl,_bin = map(int(x) for x in args.key.split(',')) 
else:
    _bbl,_bin = 1011250025,1028637 

print("bbl,bin = ",_bbl,_bin)

agent = DataClient(**dataconf)
t0 = time.time()
if args.mode == 'summary':
    r = agent.get_summary(_bbl,_bin)
elif args.mode == 'contacts':
    r = agent.get_contacts(_bbl,_bin)
else:
    r = agent.get_summary(_bbl,_bin)
delta = 1000 * (time.time() - t0)

print("dt = %.2f ms" % delta)
print(json.dumps(r,indent=True,sort_keys=True))

