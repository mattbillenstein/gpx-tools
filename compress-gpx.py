#!/usr/bin/env python3

# make a gpx smaller by removing some lat/lon accuracy, elevation, and time
# data
#
# this removes unneeded whitespace as well - you can use "xmllint --format
# <file>" if you like the pretty version

import os
import os.path
import sys

import xmltodict

# six digits good to ~0.11m - 4.33in, five good to about 1.1m,
# four good to about 11m
latlonfmt = '%.5f'

def getlist(elem, key):
    L = elem.get(key, [])
    if not isinstance(L, list):
        L = [L]
    return L

def main(args):
    for fname in args:
        basename = os.path.splitext(os.path.split(fname)[-1])[0]
        
        with open(fname, 'rb') as f:
            doc = xmltodict.parse(f)

        gpx = doc['gpx']

        for wpt in getlist(gpx, 'wpt'):
            for k in ('@lat', '@lon'):
                wpt[k] = latlonfmt % (float(wpt[k]))

        for trk in getlist(gpx, 'trk'):
            # remove repeated links
            links = getlist(trk, 'link')
            if links:
                newlinks = {}
                for link in links:
                    newlinks[link['@href']] = link
                links = list(newlinks.values())
                trk['link'] = links

            for trkseg in getlist(trk, 'trkseg'):
                trkpts = []
                last = None
                for trkpt in getlist(trkseg, 'trkpt'):
                    for k in ('@lat', '@lon'):
                        trkpt[k] = latlonfmt % (float(trkpt[k]))

                    for k in ('ele', 'time'):
                        trkpt.pop(k, None)

                    # filter out duplicate points
                    pt = (trkpt['@lat'], trkpt['@lon'])
                    if pt != last:
                        trkpts.append(trkpt)
                    last = pt

                if trkpts:
                    trkseg['trkpt'] = trkpts

        with open(f'{basename}-compressed.gpx', 'w') as f:
            f.write(xmltodict.unparse(doc))


if __name__ == '__main__':
    main(sys.argv[1:])
