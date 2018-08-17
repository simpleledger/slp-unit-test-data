#!/usr/bin/env python3

import json

def reindent(fname):
    with open(fname) as f:
        data = json.load(f)
    with open(fname,'w') as f:
        json.dump(data, f, indent=1)

reindent('script_tests.json')
