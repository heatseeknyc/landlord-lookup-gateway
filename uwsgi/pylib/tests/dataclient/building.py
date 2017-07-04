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
    with open("tdata/building.yaml","rtU") as f:
        pairs = yaml.load(f)
    print("that be %d test cases." % len(pairs))
    dotests(agent,pairs)
    print("done.")

def evaltest(agent,r):
    print("::: eval r = %s" % r)
    print("::: eval query = %s" % r['query'])
    print("::: eval expected = %s" % r['result'])
    _bbl = r['query'].get('bbl')
    _bin = r['query'].get('bin')
    expected = r['result']
    bldg_list = agent.get_building(_bbl,_bin)
    print("building.type = %s" % type(bldg_list))
    # print("building.len = %d" % len(bldg_list))
    print("building = %s" % bldg_list)
    status = compare(bldg_list,expected)
    print("status = %s" % status)

def dotests(agent,pairs):
    for r in pairs:
        evaltest(agent,r)

if __name__ == '__main__':
    main()

