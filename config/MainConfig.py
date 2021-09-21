from os.path import join
from config.params import common

releases_folder = "/data/COAPS_Net/work/ozavala/CARIBBEAN_marine_debris/release_locations_global"

def get_config():
    config= {
        common.vector_fields_folder:"/nexsan/people/xbxu/HYCOM/GLBv0.08",  # Path to currents/winds
        # Path to global marine litter (ocean parcels)
        common.global_debris_folder: "/Net/work/ozavala/WorldLitterOutput/TEN_YEARS/YesWinds_YesDiffusion_NoUnbeaching",
        common.location_folder:"/data/UN_Litter_data/HYCOM/data/release_locations", # Where the release locations are specified
        common.output_folder:"outputs",
        common.lat_files:[join(releases_folder,x) for x in ["coasts_all_y.csv", "rivers_all_y.csv"]],
        common.lon_files:[join(releases_folder,x) for x in ["coasts_all_x.csv", "rivers_all_x.csv"]],
    }
    return config