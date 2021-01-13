import sys
import pandas as pd
import csv

from CatapultData import CatapultData
from geopy.distance import great_circle 


sys.path.append('/home/bepro/bepro-python')
from bepy.models import MatchVideo
from bepy.transform import Transform

import cv2
import mmcv
import colorsys

import os
import glob

def create_unique_color_float(tag, hue_step=0.41):
    h, v = (tag * hue_step) % 1, 1. - (int(tag * hue_step) % 4) / 5.
    r, g, b = colorsys.hsv_to_rgb(h, 1., v)
    return r, g, b

def create_unique_color_uchar(tag, hue_step=0.41):
    r, g, b = create_unique_color_float(tag, hue_step)
    return int(255*r), int(255*g), int(255*b)

def convert_catapult(path, match_id, path2video):

    baseLat = 36.36567400000021
    baseLng = 127.32549000000017
    
    match_video = MatchVideo.load(match_id)

    transform = Transform(
        match_video.video.camera_recording["parameter"],
        match_video.video.camera_recording["extrinsic_json"],
        match_video.video.camera_recording["stitching_json"],
    )

    video = mmcv.VideoReader(path2video)
    h, w = video[0].shape[0], video[0].shape[1] 
    print ('image size : (%d,%d)' % (h,w))

    csv_files = glob.glob("%s/*.csv" % (path))

    gps_coords_im_all = []

    for path in csv_files:
        print (path)

        data = []
        gps_coords_im = []

        with open(path, "r") as csvfile: 
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')

            for row in reader:
                if len(row) == 0:
                    break

                line = row[0].split(',')

                if (len(line) <= 3):
                    continue

                cd = CatapultData(line)
                data.append(cd)

        print ('-> converting GPS to image coordinates')

        for d in data:
            x = great_circle((baseLat, baseLng), (d.latLng[0], baseLng)).m
            y = great_circle((baseLat, baseLng), (baseLat, d.latLng[1])).m

            x = x / transform.parameter.get("ground_width")
            y = y / transform.parameter.get("ground_height")

            px, py = transform.ground_to_video(x, y, 0)
            gps_coords_im.append((px*w, py*h))

        print ('number of GPS datapoints: %d' % (len(gps_coords_im)))

        gps_coords_im_all.append(gps_coords_im)

    out_size = (1700, 520)
    vout = cv2.VideoWriter('./catapult_out.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 25, out_size)

    start_frame = 1680
    gi = 0

    for index in range(start_frame, start_frame+6000):
        if index % 200 == 0:
            print ('f: %d' % (index+1))

        frame = video[index]

        for l, gpsd in enumerate(gps_coords_im_all):
            colour = create_unique_color_uchar(l+1)
            x,y = gpsd[gi]
            cv2.circle(frame, (int(x), int(y)), 5, colour, 5)
            cv2.putText(frame, "P%d"%(l+1), (int(x+8), int(y+8)), cv2.FONT_HERSHEY_PLAIN, 2, colour, 2)

        if index % 3 == 0:
            gi = gi + 1

        if index >= 4000:
            vout.write(cv2.resize(frame, out_size))

    vout.release()

if __name__ == "__main__":
    convert_catapult(sys.argv[1], int(sys.argv[2]), sys.argv[3])
