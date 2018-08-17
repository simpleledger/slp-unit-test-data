#!/usr/bin/env python3

import json

def reindent(fname):
    """ Load then re-dump a json file with standard format (use for cleanup before committing). """
    with open(fname) as f:
        data = json.load(f)
    with open(fname,'w') as f:
        json.dump(data, f, indent=1)

reindent('script_tests.json')
