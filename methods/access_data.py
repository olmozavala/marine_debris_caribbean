#%%
from config.MainConfig import get_config
from config.params import common
import pandas as pd
import numpy as np
from os.path import join
import os
import xarray as xr
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
from proj_utils.proj_io import save_obj

config = get_config()
part_per_release = 32300

global_output_folder = config[common.global_debris_folder]
all_files = os.listdir(global_output_folder)
all_files.sort()
bbox = [0, 30, -99, -49] # minlat, maxlat, minlon, maxlon

def get_single_release_data(year, month):
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
    :param bbox:
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
    last_month = np.datetime64(F'{year}-{month+1:02d}')
    first_date = np.datetime64(F'{year}-{month:02d}-01')
    last_date = np.datetime64(F'{year}-{month+1:02d}-01')

    month_data = {}
    # Iterate over the months that will provide data to the desired month
    while c_month < last_month:
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

if __name__ == "__main__":
    # data = get_single_release_data(2018,11)
    # end_date = np.datetime64(F'2018-12-01')
    # idx = data.time == end_date
    # x = 1
    # all_times = np.unique(data.time)
    output_folder = config[common.caribbean_from_global_folder]

    for c_year in range(2010, 2020):
        for first_month in range(1, 13):
            c_date = datetime.date(c_year, first_month, 1)
            # data_by_month = {}
            last_date = datetime.date(c_year, first_month+1, 1) if first_month < 12 else datetime.date(c_year+1, 1, 1)
            print(F"############ {c_year}-{first_month} ###############")
            data_by_month = get_all_particles_per_month_and_region(c_date.year,c_date.month, bbox)
            # while c_date < last_date:
            #     date_str = c_date.strftime("%Y-%m-%d")
            #     print(F"---------- {date_str} -----------")
            #     # data = get_all_particles_per_day_and_region(c_date.year,c_date.month,c_date.day, bbox)
            #     data = get_all_particles_per_month_and_region(c_date.year,c_date.month, bbox)
            #     data_by_month.update(data)
            #     # plt.scatter(data[date_str]['lon'], data[date_str]['lat'])
            #     # plt.axis('equal')
            #     # plt.title(date_str)
            #     # plt.show()
            #     c_date += timedelta(days=1)

            file_name = join(output_folder,F"{c_year}_{first_month}.pkl")
            save_obj(data_by_month, file_name)
