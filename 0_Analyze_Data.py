from config.MainConfig import get_config
from config.params import common
from os.path import join
import geoviews as gv
import geoviews.feature as gf
import xarray as xr
from cartopy import crs

gv.extension('bokeh')

def display_fields(config):


if __name__ == "__main__":
    config = get_config()
    display_fields(config)

