import pandas as pd
import numpy as np
from os.path import join
import os
import xarray as xr
import datetime
from datetime import timedelta
import scipy

file_name_coast = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/CARIBBEAN_MarineLitter/data/processed/COASTS_all_w.cvs"
file_name_rivers = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/CARIBBEAN_MarineLitter/data/processed/RIVERS_all_w.cvs"
coasts_w = pd.read_csv(file_name_coast, header=None, names=['coasts_w'])
rivers_w = pd.read_csv(file_name_rivers, header=None, names=['rivers_w'])
# mat_file =  "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/CARIBBEAN_MarineLitter/data/processed/min_distance_to_country_ini.mat"
# mat = scipy.io.loadmat(mat_file)
all_w = np.array([*coasts_w.iloc[:,0].values, *rivers_w.iloc[:,0].values])
x = 1
