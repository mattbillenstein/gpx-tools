#!/usr/bin/env python3

# compute some stats on a given gpx file

import os
import os.path
import sys

import xmltodict

from math import radians, cos, sin, asin, sqrt

METERS_TO_FEET = 3.28084

def haversine(lat1, lon1, lat2, lon2):
    R = 3959.87433 # this is in miles.  For Earth radius in kilometers use 6372.8 km

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))

    return R * c

def haversine_trkpt(pt1, pt2):
    return haversine(
        float(pt1['@lat']),
        float(pt1['@lon']),
        float(pt2['@lat']),
        float(pt2['@lon']),
    )

def getlist(elem, k):
    L = elem.get(k, [])
    if not isinstance(L, list):
        L = [L]
    return L

def main(args):
    print('%-40s %10s %10s %10s %10s %10s %10s' % ('Track', 'Miles', 'TotMiles', 'UpFeet', 'DownFeet', 'dElev', 'Elev'))

    for fname in args:
        with open(fname, 'rb') as f:
            doc = xmltodict.parse(f)

        totaldist = 0.0
        totalelev = 0.0

        for trk in sorted(getlist(doc['gpx'], 'trk') + getlist(doc['gpx'], 'rte'), key=lambda x: x['name']):
            last = None

            if 'trkseg' in trk:
                pts = []
                for trkseg in getlist(trk, 'trkseg'):
                    pts += getlist(trkseg, 'trkpt')
            else:
                pts = getlist(trk, 'rtept')

            dist = 0.0
            up = 0.0
            down = 0.0

            has_ele = all('ele' in _ for _ in pts)

            for pt in pts:
                if last:
                    dist += haversine_trkpt(last, pt)

                    # missing elevations seem to be -19999.0
                    if has_ele and pt['ele'] != '-19999.0' and last['ele'] != '-19999.0':
                        elev = (float(pt['ele']) - float(last['ele'])) * METERS_TO_FEET
                        if elev > 0.0:
                            up += elev
                        else:
                            down += elev
                elif has_ele:
                    # set initial elevation
                    totalelev = float(pt['ele']) * METERS_TO_FEET

                last = pt

            elev = up + down

            totaldist += dist
            totalelev += elev

            print('%-40s %10.1f %10.1f %10.1f %10.1f %10.1f %10.1f' % (trk['name'].replace(' ', '_'), dist, totaldist, up, down, elev, totalelev))

if __name__ == '__main__':
    main(sys.argv[1:])
