#!/usr/bin/env python
import sys
import yaml
import time, argparse
import simplejson as json
from lookuptool.dataclient import DataClient
from tests.util import compare

parser = argparse.ArgumentParser()
parser.add_argument("--mode", help="what to pull")
parser.add_argument("--key", help="BBL,BIN pair to use as primary key")
args = parser.parse_args()

def init_agent(configpath):
    dataconf = json.loads(open(configpath,"r").read())
    return DataClient(**dataconf)

def main():
    agent = init_agent("config/postgres.json")
    with open("tdata/taxlot.yaml","rtU") as f:
        pairs = yaml.load(f)
    print("that be %d test cases." % len(pairs))
    dotests(agent,pairs)
    print("done.")

def evaltest(agent,r):
    print(r)
    query = r['query']
    result = r['result']
    taxlot = agent.get_taxlot(bbl=query['bbl'])
    print("taxlot = %s" % taxlot)
    status = compare(taxlot,result)
    print("status = %s" % status)

def dotests(agent,pairs):
    for r in pairs:
        evaltest(agent,r)

if __name__ == '__main__':
    main()

