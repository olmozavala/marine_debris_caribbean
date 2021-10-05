from enum import Enum

class GlobalModel(Enum):
    vector_fields_folder=1
    global_debris_folder=2
    caribbean_from_global_folder = 3
    unbeach_file = 10

    location_folder=4
    output_folder=5

    lat_files=6
    lon_files=7
    dt=20
    output_freq=21
    repeat_release=22

class RegionalModel(Enum):
    bbox=1
