#!/usr/bin/env python
import sys
import yaml
import time, argparse
import simplejson as json
from gateway.dataclient import DataClient
from tests.util import compare

LOUD,FAIL = False,False

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

def evaltest(agent,r):
    query = r['query']
    result = r['result']
    if LOUD:
        print("query = %s" % query)
    taxlot = agent.get_taxlot(bbl=query['bbl'])
    if LOUD:
        print("result = %s" % result)
        print("taxlot = %s" % taxlot)
    compare(taxlot,result)

def dotests(agent,pairs):
    for i,r in enumerate(pairs):
        status = evaltest(agent,r)
        print("status[%d] = %s" % (i,status))

def main():
    global LOUD
    args = parse_args()
    LOUD = args.loud
    FAIL = args.fail
    agent = init_agent("config/postgres.json")
    with open("tdata/dataclient/taxlot.yaml","rtU") as f:
        pairs = yaml.load(f)
    print("that be %d test cases." % len(pairs))
    dotests(agent,pairs)
    print("done.")

if __name__ == '__main__':
    main()

