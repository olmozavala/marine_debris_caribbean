import datetime

import numpy as np
import xarray as xr
from os.path import  join

##
def append_to_array(old, new):
    start_idx = old.shape[1] - new.shape[1]
    new_lat = np.full((ds.lat.shape[0], lat.shape[1]), np.nan)
    new_lat[:, start_idx:] = ds.lat
    lat = np.concatenate([lat, new_lat])

##

output_folder = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/Particle_viz/ExampleData"
input_folder = "/nexsan/people/pmiron/projects_mars/caribbean-marine-litter/data/output/cm_mpw"

start_release = datetime.datetime.strptime("2021-10-01", "%Y-%m-%d")
end_release = datetime.datetime.strptime("2021-12-01", "%Y-%m-%d")

cur_date = start_release
y = start_release.year
m = start_release.month
all_files = []

while cur_date < end_release:
    # I modify it so that it takes the names from heere NOT from the config file
    file_name = F"cm_mpw_{y}-{m:02d}-01.nc"
    print(f"Agregating file {file_name}")
    if m == 12:
        m = 1
        y += 1
    else:
        m += 1
    ds = xr.open_dataset(join(input_folder, file_name))
    if cur_date == start_release:
        lat = ds.lat
        lon = ds.lon
        atime = ds.time
        traj = ds.traj
    else:
        start_idx = lat.shape[1] - ds.lat.shape[1]
        new_lat = np.full((ds.lat.shape[0], lat.shape[1]), np.nan)
        new_lat[:, start_idx:] = ds.lat
        lat = np.concatenate([lat, new_lat])
    cur_date = datetime.datetime.strptime(F"{y}-{m}-01", "%Y-%m-%d")

##
ds = xr.Dataset(
    {
        # "time": (("time"), atime),
        "lat": (("traj", "obs"), lat),
        "lon": (("traj", "obs"), lon),
    },
    {"obs": atime, "traj":traj},
)

# ds = xr.merge([xr.open_dataset(x) for x in all_files])
x = 1
