#!/usr/bin/env python
import sys
import yaml
import time, argparse
import simplejson as json
from lookuptool.dataclient import DataClient

parser = argparse.ArgumentParser()
parser.add_argument("--mode", help="what to pull")
parser.add_argument("--key", help="BBL,BIN pair to use as primary key")
args = parser.parse_args()

def init_agent(configpath):
    dataconf = json.loads(open(configpath,"r").read())
    return DataClient(**dataconf)

def main():
    agent = init_agent("config/postgres.json")
    with open("tests/data/building.yaml","rtU") as f:
        pairs = yaml.load(f)
    print("that be %d test cases." % len(pairs))

if __name__ == '__main__':
    main()

sys.exit(1)
"""
print(json.dumps(r,indent=4,sort_keys=True))
"""

