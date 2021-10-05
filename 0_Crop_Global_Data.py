import datetime
from os.path import join
from proj_io.common_io import save_obj
from config.MainConfig import get_config
from config.params import GlobalModel, RegionalModel
from proj_io.global_data_io import get_all_particles_per_month_and_region

# This code is used to generate a new database that contains all the particles
# per day of a subregion from the global output. This new database should make it much easier
# to work with the region.

if __name__ == "__main__":
    config = get_config()

    output_folder = config[GlobalModel.caribbean_from_global_folder]
    bbox = config[RegionalModel.bbox]
    # Iterates over all the years of interest
    for c_year in range(2011, 2020):
        # Iterate over all the months for each year
        for first_month in range(1, 13):
            c_date = datetime.date(c_year, first_month, 1)
            print(F"############ {c_year}-{first_month} ###############")
            data_by_month = get_all_particles_per_month_and_region(c_date.year,c_date.month, bbox)
            file_name = join(output_folder,F"{c_year}_{first_month}.pkl")
            save_obj(data_by_month, file_name)
