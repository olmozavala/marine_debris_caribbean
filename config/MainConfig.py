from os.path import join
from config.params import GlobalModel, RegionalModel
from datetime import timedelta

releases_folder = "/data/COAPS_Net/work/ozavala/CARIBBEAN_marine_debris/release_locations_global"

def get_config():
    config= {
        GlobalModel.vector_fields_folder: "/nexsan/people/xbxu/HYCOM/GLBv0.08",  # Path to currents/winds
        # Path to global marine litter (ocean parcels)
        GlobalModel.global_debris_folder: "/Net/work/ozavala/CARIBBEAN_marine_debris/ten_year_lagrangian_marine_debris",
        # Path to regional marine litter
        GlobalModel.caribbean_from_global_folder: "/Net/work/ozavala/CARIBBEAN_marine_debris/caribbean_region_from_global_v2",
        # Path to regional marine litter
        GlobalModel.location_folder: "/Net/work/ozavala/CARIBBEAN_marine_debris/release_locations", # Where the release locations are specified
        GlobalModel.lat_files:[join(releases_folder, x) for x in ["coasts_all_y.csv", "rivers_all_y.csv"]],
        GlobalModel.lon_files:[join(releases_folder, x) for x in ["coasts_all_x.csv", "rivers_all_x.csv"]],
        GlobalModel.output_folder: "/data/UN_Litter_data/output/TESTING",
        GlobalModel.unbeach_file: "/data/COAPS_Net/work/ozavala/CARIBBEAN_marine_debris/unbeach_file_global/unbeaching.nc",

        GlobalModel.dt: timedelta(hours=1), # 1 hour
        GlobalModel.output_freq: timedelta(hours=24),  # 24
        # GlobalModel.repeat_release: timedelta(hours=0),  # 61
        GlobalModel.repeat_release: None,

        RegionalModel.bbox: [0, 30, -99, -49], # minlat, maxlat, minlon, maxlon
    }
    return config