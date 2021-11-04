from config.MainConfig import get_config
from config.params import GlobalModel
import numpy as np
from os.path import join
import os
import xarray as xr
import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPoint

config = get_config()
part_per_release = 32300

global_output_folder = config[GlobalModel.global_debris_folder]
# bbox = config[GlobalModel.bbox]
all_files = os.listdir(global_output_folder)
all_files.sort()

def get_single_release_data(year, month):
    """
    It returns the dataset of the selected release year and month
    :return: xarray dataset
    """
    c_file = [x for x in all_files if F"{year}_{month:02d}" in x][0]
    # print(F"Working with {c_file}")
    xrds = xr.open_dataset(join(global_output_folder,c_file))
    return xrds

def get_all_particles_per_day_and_region(year, month, day, bbox):
    """
    This function will obtain all the particles for a particular day and region.
    :param year:
    :param month:
    :param day:
    :param bbox: list minlat, maxlat, minlon, maxlon
    :return:
    """
    c_date = np.datetime64('2010-01')
    end_month = np.datetime64(F'{year}-{month+1:02d}')
    end_date = np.datetime64(F'{year}-{month:02d}-{day:02d}')
    release_date = []
    count_per_release = []
    imonth = 0
    while c_date < end_month:
        # print(F"Reading date {c_date}")
        data = get_single_release_data(c_date.astype(object).year, c_date.astype(object).month)
        idx = data.time == end_date
        # final_data[0,part_per_release*imonth:part_per_release*(imonth+1)] = data.lat.data[idx]
        # final_data[1,part_per_release*imonth:part_per_release*(imonth+1)] = data.lon.data[idx]
        idx_lat = np.logical_and(data.lat.data[idx] >= bbox[0], data.lat.data[idx] <= bbox[1])
        idx_lon = np.logical_and(data.lon.data[idx] >= bbox[2], data.lon.data[idx] <= bbox[3])
        idx_comb = np.logical_and(idx_lat, idx_lon)
        c_lats = data.lat.data[idx][idx_comb]
        c_lons = data.lon.data[idx][idx_comb]
        if imonth == 0:
            lats = c_lats
            lons =  c_lons
            orig_pos = np.where(idx_comb)
        else:
            lats = np.append(lats, c_lats)
            lons = np.append(lons, c_lons)
            orig_pos = np.append(orig_pos,np.where(idx_comb))
        release_date.append(c_date)
        count_per_release.append(len(c_lats))
        c_date = c_date + np.timedelta64(1, 'M')
        imonth += 1
    # print(F"Done reading particles for a particular day {end_date} and region {bbox}")
    return {str(end_date):{'lat':lats, 'lon':lons, 'orig_pos':orig_pos, 'release_date':release_date, 'count_per_release':count_per_release}}

def get_all_particles_per_month_and_region(year, month, bbox):
    """
    This function will obtain all the particles for a particular month and region.
    :param year:
    :param month:
    :param day:
    :param bbox:
    :return:
    """
    c_month = np.datetime64('2010-01')  # This is the beginning of the model (always the same)
    last_month = np.datetime64(F'{year}-{month+1:02d}') if month < 12 else np.datetime64(F'{year+1}-01')
    last_date = np.datetime64(F'{year}-{month+1:02d}-01') if month < 12 else np.datetime64(F'{year+1}-01-01')

    month_data = {}
    # Iterate over the months that will provide data to the desired month
    while c_month < last_month:
        print(F"============ {str(c_month)} ===============")
        data = get_single_release_data(c_month.astype(object).year, c_month.astype(object).month)
        c_date = np.datetime64(F'{year}-{month:02d}-01')

        # Iterate over the dates of the desired month
        while c_date < last_date:
            c_date_str = str(c_date)
            print(F"Working with date {c_date_str}")
            idx = data.time == c_date

            release_date = []
            count_per_release = []
            idx_lat = np.logical_and(data.lat.data[idx] >= bbox[0], data.lat.data[idx] <= bbox[1])
            idx_lon = np.logical_and(data.lon.data[idx] >= bbox[2], data.lon.data[idx] <= bbox[3])
            idx_comb = np.logical_and(idx_lat, idx_lon)
            c_lats = data.lat.data[idx][idx_comb]
            c_lons = data.lon.data[idx][idx_comb]
            c_orig_pos = np.where(idx_comb)
            c_release_date = c_month
            c_count_per_release = len(c_lats)
            if c_date_str in month_data.keys():
                month_data[c_date_str]['lat'] = np.append(month_data[c_date_str]['lat'], c_lats)
                month_data[c_date_str]['lon'] = np.append(month_data[c_date_str]['lon'], c_lons)
                month_data[c_date_str]['orig_pos'] = np.append(month_data[c_date_str]['orig_pos'], c_orig_pos)
                month_data[c_date_str]['release_date'] = np.append(month_data[c_date_str]['release_date'], c_release_date)
                month_data[c_date_str]['count_per_release'] = np.append(month_data[c_date_str]['count_per_release'], c_count_per_release)
            else:
                month_data.update({c_date_str:{
                    'lat':c_lats, 'lon':c_lons,
                    'orig_pos':c_orig_pos,
                    'release_date':c_release_date,
                    'count_per_release':c_count_per_release}})
            c_date = c_date + np.timedelta64(1, 'D')

        c_month += np.timedelta64(1, 'M')
    return month_data

def get_all_particles_per_month_in_caribbean_region(year, month):
    """
    This function will obtain all the particles for a particular month and region.
    :param year:
    :param month:
    :param day:
    :param bbox:
    :return:
    """
    c_month = np.datetime64('2010-01')  # This is the beginning of the model (always the same)
    last_month = np.datetime64(F'{year}-{month+1:02d}') if month < 12 else np.datetime64(F'{year+1}-01')
    last_date = np.datetime64(F'{year}-{month+1:02d}-01') if month < 12 else np.datetime64(F'{year+1}-01-01')

    bbox= [0, 30, -99, -49]

    roi = gpd.read_file("/Net/work/ozavala/CARIBBEAN_marine_debris/countries_info/countries_oz/Caribbean_ROI.shp")
    roi_polygon = roi.geometry[0]

    month_data = {}
    # Iterate over the months that will provide data to the desired month
    while c_month < last_month:
        print(F"============ {str(c_month)} ===============")
        data = get_single_release_data(c_month.astype(object).year, c_month.astype(object).month)
        c_date = np.datetime64(F'{year}-{month:02d}-01')

        # Iterate over the dates of the desired month
        while c_date < last_date:
            c_date_str = str(c_date)
            print(F"Working with date {c_date_str}")
            idx = data.time == c_date

            release_date = []
            count_per_release = []
            idx_lat = np.logical_and(data.lat.data[idx] >= bbox[0], data.lat.data[idx] <= bbox[1])
            idx_lon = np.logical_and(data.lon.data[idx] >= bbox[2], data.lon.data[idx] <= bbox[3])
            idx_comb = np.logical_and(idx_lat, idx_lon)
            c_lats = data.lat.data[idx][idx_comb]
            c_lons = data.lon.data[idx][idx_comb]
            c_orig_pos = np.where(idx_comb)[0]
            # Restrinct to specified domain
            # c_locs = [Point(c_lons[i],c_lats[i]).intersects(roi_polygon) for i in range(len(c_lats))]
            c_locs = [roi_polygon.intersects(Point(c_lons[i],c_lats[i])) for i in range(len(c_lats))]
            f_lats = c_lats[c_locs]
            f_lons = c_lons[c_locs]
            f_orig_pos = c_orig_pos[c_locs]
            c_release_date = c_month
            c_count_per_release = len(f_lats)
            if c_date_str in month_data.keys():
                month_data[c_date_str]['lat'] = np.append(month_data[c_date_str]['lat'], f_lats)
                month_data[c_date_str]['lon'] = np.append(month_data[c_date_str]['lon'], f_lons)
                month_data[c_date_str]['orig_pos'] = np.append(month_data[c_date_str]['orig_pos'], f_orig_pos)
                month_data[c_date_str]['release_date'] = np.append(month_data[c_date_str]['release_date'], c_release_date)
                month_data[c_date_str]['count_per_release'] = np.append(month_data[c_date_str]['count_per_release'], c_count_per_release)
            else:
                month_data.update({c_date_str:{
                    'lat':f_lats, 'lon':f_lons,
                    'orig_pos':f_orig_pos,
                    'release_date':c_release_date,
                    'count_per_release':c_count_per_release}})
            c_date = c_date + np.timedelta64(1, 'D')

        c_month += np.timedelta64(1, 'M')
    return month_data
