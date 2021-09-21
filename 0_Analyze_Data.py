from config.MainConfig import get_config
from config.params import common
from os.path import join
import geoviews as gv
import geoviews.feature as gf
import xarray as xr
from cartopy import crs

gv.extension('bokeh')

def display_fields(config):
    vector_fields_folder = config[common.vector_fields_folder]
    xrds = xr.open_dataset(join(vector_fields_folder, "Winds_25p_def_15deg_hycom_GLBv0.08_536_2010010112_t015.nc"))
    geods = gv.Dataset(xrds, ['longitude', 'latitude', 'time'], 'U_combined', crs=crs.PlateCarree())
    images = geods.to(gv.Image)


if __name__ == "__main__":
    config = get_config()
    display_fields(config)

