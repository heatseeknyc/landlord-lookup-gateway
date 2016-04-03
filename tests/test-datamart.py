import sys, time, argparse
import simplejson as json
from lookuptool.agent import DataMartAgent

parser = argparse.ArgumentParser()
parser.add_argument("--mode", help="what to pull")
parser.add_argument("--bbl", help="BBL to use as primary key", type=int)
args = parser.parse_args()

configpath = "config/postgres.json"
dataconf = json.loads(open(configpath,"r").read())

bbl = args.bbl if args.bbl else 1011250025 
print("bbl = ",bbl)

agent = DataMartAgent(**dataconf)
t0 = time.time()
if args.mode == 'everything':
    r = agent.get_everything(bbl)
elif args.mode == 'details':
    r = agent.get_details(bbl)
else:
    r = agent.get_summary(bbl)
delta = 1000 * (time.time() - t0)

print("dt = %.2f ms" % delta)
print(json.dumps(r,indent=True,sort_keys=True))

