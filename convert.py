import sys
import pandas as pd
import googlemaps
from itertools import tee

import csv
from CatapultData import CatapultData

from geopy.distance import great_circle 

def convert_catapult(path):
    data = []
    with open(path, 'rb') as csvfile: 
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')

        for i,row in enumerate(reader):
            if len(row) == 0:
                break

            line = row[0].split(',')

            if (len(line) <= 3):
                continue

            cd = CatapultData(line)
            data.append(cd)
    
    baseLat = 36.36567400000021
    baseLng = 127.32549000000017
    
    for d in data:
        x = great_circle((baseLat, baseLng), (d.latLng[0], baseLng)).m
        y = great_circle((baseLat, baseLng), (baseLat, d.latLng[1])).m
        print (x,y)

if __name__ == "__main__":
    convert_catapult(sys.argv[1])
