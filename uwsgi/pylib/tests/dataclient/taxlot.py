import sys
import yaml
import time, argparse
import simplejson as json
from gateway.dataclient import DataClient
from tests.util import compare, displaypath

ARGS = None

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loud", help="be loud", action="store_true")
    parser.add_argument("--fail", help="fail fast", action="store_true")
    parser.add_argument("--mode", help="what to pull")
    parser.add_argument("--key", help="BBL,BIN pair to use as primary key")
    return parser.parse_args()

def init_agent(configpath):
    dataconf = json.loads(open(configpath,"r").read())
    return DataClient(**dataconf)

def perform(agent,query):
    return agent.get_taxlot(bbl=query['bbl'])

def evaltest(agent,r):
    query = r['query']
    result = r['result']
    if ARGS.loud:
        print("query = %s" % query)
    try:
        taxlot = perform(agent,query)
    except Exception as e:
        print("FAILED: %s" % e)
        if ARGS.fail:
            raise e
        return False
    if ARGS.loud:
        print("result = %s" % result)
        print("taxlot = %s" % taxlot)
    return compare(taxlot,result)

def dotests(agent,pairs):
    for i,r in enumerate(pairs):
        if r.get('skip'):
            print("status[%d] = SKIP" % i)
            continue
        path = evaltest(agent,r)
        status,longpath = displaypath(path)
        if status:
            print("status[%d] = ok" % i)
        else:
            print("status[%d] = FAILED %s" % (i,longpath))
        if ARGS.fail and not status:
            print("FAILED test %d" % i)
            sys.exit(1)

def main():
    global ARGS
    ARGS = parse_args()
    agent = init_agent("config/postgres.json")
    with open("tdata/dataclient/taxlot.yaml","rtU") as f:
        pairs = yaml.load(f)
    print("that be %d test cases." % len(pairs))
    dotests(agent,pairs)
    print("done.")

if __name__ == '__main__':
    main()

