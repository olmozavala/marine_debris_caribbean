from config.MainConfig import get_config
from config.params import GlobalModel
from proj_io.common_io import load_obj, save_obj
from os.path import join
import numpy as np
import os
import xarray as xr
from calendar import monthrange
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import time
import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPoint

config = get_config()
input_folder = "/data/COAPS_Net/work/ozavala/CARIBBEAN_marine_debris/caribbean_region_from_global"
roi = gpd.read_file("/Net/work/ozavala/CARIBBEAN_marine_debris/countries_info/countries_oz/Caribbean_ROI.shp")
roi_polygon = roi.geometry[0]

file_names = os.listdir(input_folder)

for c_file in file_names:
    c_path = join(input_folder, c_file)
    c_data = load_obj(c_path)
    for c_date, row in c_data.items():
        print(c_date)
        c_locs = MultiPoint([(row['lon'][i],row['lat'][i]) for i in range(len(row['lat']))])
        t = time.time()
        c_locs = [Point(row['lon'][i],row['lat'][i]).intersects(roi_polygon) for i in range(len(row['lat']))]
        print(time.time() - t)
        t = time.time()
        c_locs = [roi_polygon.intersects(Point(row['lon'][i],row['lat'][i])) for i in range(len(row['lat']))]
        print(time.time() - t)
        exit()
