import datetime
import os
from os.path import join
import xarray as xr

from img_viz.common import create_folder
from proj_io.common_io import save_obj
from config.MainConfig import get_config
from config.params import GlobalModel, RegionalModel
from proj_io.global_data_io import *
from shapely.geometry import Polygon, Point, MultiPoint
import time

# This code is used to generate a new database that contains all the particles
# per day of a subregion from the global output. This new database should make it much easier
# to work with the region.

if __name__ == "__main__":
    config = get_config()

    input_folder = config[GlobalModel.global_debris_folder]
    output_folder = "/data/COAPS_Net/work/ozavala/CARIBBEAN_marine_debris/ten_year_lagrangian_marine_debris_cropped"

    roi = gpd.read_file("/Net/work/ozavala/CARIBBEAN_marine_debris/countries_info/countries_oz/Caribbean_ROI.shp")
    roi_polygon = roi.geometry[0]

    all_files = os.listdir(input_folder)
    all_files = [x for x in all_files if x.find('nc') != -1]
    all_files.sort(reverse=True)
    for c_file in all_files:
        print(F"Working with file {c_file}")
        c_path = join(input_folder, c_file)
        data = xr.open_dataset(c_path)

        tot_particles = data.lat.shape[0]
        final_particles = []
        for c_particle in range(tot_particles):
            if c_particle % 200 == 0:
                print(c_particle)

            c_lats = data.lat.values[c_particle,:]
            c_lons = data.lon.values[c_particle,:]

            # intersects = roi_polygon.intersects(MultiPoint([(c_lons[i], c_lats[i]) for i in range(len(c_lats))]))
            intersects =MultiPoint([(c_lons[i], c_lats[i]) for i in range(len(c_lats))]).intersects(roi_polygon)
            if intersects:
                final_particles.append(c_particle)

        ds = xr.Dataset(
            {
                "lat": (("traj", "obs"), data.lat.values[final_particles,:]),
                "lon": (("traj", "obs"), data.lon.values[final_particles,:]),
                "time": (("traj", "obs"), data.time.values[final_particles,:]),
            },
            {"traj": data.traj.values[final_particles], "obs": data.obs.values},
        )
        ds.to_netcdf(join(output_folder, c_file))