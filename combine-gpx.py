#!/usr/bin/env python3

# combine gpx files, google maps only allows 10 layers, so combining many small
# gpx into a single file can help get them all into a single map

import os
import os.path
import sys

import xmltodict

def getlist(elem, key):
    L = elem.get(key, [])
    if not isinstance(L, list):
        L = [L]
    return L

def main(args):
    names = []
    combined = None

    for fname in args:
        basename = os.path.splitext(os.path.split(fname)[-1])[0]
        names.append(basename.replace(' ', '_'))
        
        with open(fname, 'rb') as f:
            doc = xmltodict.parse(f)

        gpx = doc['gpx']

        if not combined:
            combined = doc
            for k in ('wpt', 'trk'):
                gpx[k] = getlist(gpx, k)
            continue

        # hack, combine attributes - similar gpx should have the same
        # extensions - meh
        for k in gpx:
            if k[0] == '@':
                combined['gpx'][k] = gpx[k]

        for k in ('wpt', 'trk'):
            combined['gpx'][k].extend(getlist(gpx, k))

    name = '-'.join(names)
    with open(f'{name}.gpx', 'w') as f:
        f.write(xmltodict.unparse(combined))


if __name__ == '__main__':
    main(sys.argv[1:])
