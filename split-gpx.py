#!/usr/bin/env python3

# split a gpx into smaller files - wpt as a separate file, then trk0, trk1, ...
# as needed

import os
import os.path
import sys

import xmltodict

# target chunk size in bytes - google maps won't import gpx > 5MB
gpx_size = 5_000_000

def main(args):
    for fname in args:
        basename = os.path.splitext(os.path.split(fname)[-1])[0]
        
        size = os.stat(fname).st_size
        parts = size // gpx_size + 1

        with open(fname, 'rb') as f:
            doc = xmltodict.parse(f)

        meta = {}
        elems = {}
        for k, v in doc['gpx'].items():
            if k[0] == '@' or k == 'metadata':
                meta[k] = v
            else:
                if isinstance(v, list):
                    elems[k] = v
                else:
                    elems[k] = [v]

        if 'wpt' in elems:
            part = {'gpx': dict(meta)}
            part['gpx']['wpt'] = elems['wpt']
            with open(f'{basename}-wpt.gpx', 'w') as f:
                f.write(xmltodict.unparse(part))

        size_part = len(elems['trk']) // parts + 1
        j = 0
        for i in range(0, len(elems['trk']), size_part):
            j += 1
            part = {'gpx': dict(meta)}
            part['gpx']['trk'] = elems['trk'][i:i+size_part]
            
            with open(f'{basename}-trk{j}.gpx', 'w') as f:
                f.write(xmltodict.unparse(part))


if __name__ == '__main__':
    main(sys.argv[1:])
