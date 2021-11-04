import glob
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy import stats
import scipy.io
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cmocean
#%%
output_folders = '/nexsan/people/pmiron/projects_mars/marine_debris_un/figs/'
data_folder = '/nexsan/people/pmiron/projects_mars/marine_debris_un/data/'
#%%
# country information
shape_folder = data_folder + 'processed/gadm36_levels_shp/'
shape_file = 'gadm36_0'
country_shp = shpreader.Reader(shape_folder + shape_file)
num_country = len(country_shp)
col_country = cm.viridis(np.arange(0,num_country));

# dictionnary for country index and name
country2id = {}
id2country = {}
for i, record in enumerate(country_shp.records()):
    country2id[record.attributes['NAME_0']] = i
    id2country[i] = record.attributes['NAME_0']
#%%
# load closest country to initial particle
closest_c = scipy.io.loadmat(data_folder + 'processed/min_distance_to_country_ini.mat')
imin0 = closest_c['imin'].squeeze() - 1 # -1 for python index
dmin0 = closest_c['dmin'].squeeze()

# weight of the particle
w = np.hstack((
    np.loadtxt(data_folder + 'processed/COASTS_all_w.cvs'),
    np.loadtxt(data_folder + 'processed/RIVERS_all_w.cvs')
)).T
#%%
imin0
#%%
# https://en.wikipedia.org/wiki/List_of_Caribbean_countries_by_population

# Validated with the names in gadm36_0 shapefile
caribbean_countries = [ # countries
    'Antigua and Barbuda', 'Bahamas', 'Barbados',
    'Cuba', 'Dominica', 'Dominican Republic',
    'Grenada', 'Haiti', 'Jamaica', 'Saint Kitts and Nevis',
    'Saint Lucia', 'Saint Vincent and the Grenadines',
    'Trinidad and Tobago',
    # dependant teritory
    'Anguilla', 'Aruba',
    'Bonaire, Sint Eustatius and Saba',
    'British Virgin Islands', 'Cayman Islands',
    'Curaçao', 'Guadeloupe', 'Martinique',
    'Montserrat', 'Puerto Rico', 'Saint-Barthélemy',
    'Saint-Martin', 'Sint Maarten',
    'Turks and Caicos Islands', 'Virgin Islands, U.S.',
    # other countries
    'Mexico', 'United States', 'Venezuela', 'Belize', 'Colombia',
    'Costa Rica', 'Guatemala', 'Guyana', 'Honduras', 'Nicaragua', 'Panama',
    'Suriname', 'Guyane'
]

# create dictionnary with the geometry of each country
caribbean_countries_geo = {}
for i, record in enumerate(country_shp.records()):
    country_i = record.attributes['NAME_0']
    if country_i in caribbean_countries:
        if record.geometry.geom_type =='Polygon':
            caribbean_countries_geo[country_i] = [record.geometry]
        else:
            caribbean_countries_geo[country_i] = record.geometry

# https://en.wikipedia.org/wiki/Caribbean
# Belize, Guyana, and Suriname are also considered part of the Caribbean
# despite  being mainland countries and they are full member states of
# the Caribbean Community and the Association of Caribbean States.
#%%
# countries with data
print('Trajectory data from:')
for country_name in caribbean_countries:
    idx = np.where(imin0 == country2id[country_name])[0]
    if idx.size:
        print('- %s' % country_name)
#%%
# which countries we don't have any data
print('No trajectory from:')
for country_name in caribbean_countries:
    idx = np.where(imin0 == country2id[country_name])[0]
    if not idx.size:
        print('- %s' % country_name)
#%% md
# Initial Particles
# - 32000 different locations
# - each location *i* is associated with a country index (*imin[i]*) and the distance (*dmin[i]*) to the coastlines
#%%
# function to plot with cartopy
def geo_map(ax):
    # ticks

    # gridlines and labels
    gl = ax.gridlines(color='k', linewidth=0.1, linestyle='-',
                      xlocs=[-90, -80, -70, -60], ylocs=[10, 20, 30],
                      draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    gl.rotate_labels = False
    gl.xpadding = 10
    gl.ypadding = 10
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())

    # add land and coastline
    #ax.add_feature(cfeature.LAND, facecolor='grey', zorder=1)
    land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                            edgecolor='face',
                                            facecolor='grey')
    ax.add_feature(land_50m)
    ax.coastlines('50m', linewidth=0.25)
    #ax.add_feature(cfeature.COASTLINE, linewidth=0.25, zorder=1)
    #ax.set_extent([-98, -78, 18, 31], crs=ccrs.PlateCarree())
    ax.set_extent([-98, -55, 8, 32], crs=ccrs.PlateCarree())

def add_colorbar(fig, ax, var, fmt=None, range_limit=None):
    """
    """
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.02, axes_class=plt.Axes)

    # change range first so it doesn't reset the format
    if range_limit:
        var.set_clim(range_limit)

    # colorbar with possible formatting for scientific format (10^)
    cb = fig.colorbar(var, cax=cax, format=fmt)
    cb.ax.tick_params(which='major', labelsize=6, length=3, width=0.5, pad=0.05)

    return cb
#%%
# 10 year simulation
folder = "/nexsan/people/ozavala/WorldLitterOutput/TEN_YEARS/YesWinds_YesDiffusion_NoUnbeaching/"
files = sorted(glob.glob(folder + "/*.nc"))

# from 2017 onward
files = files[84:]

# plot n days
plot_days = 30

# bins
binx = np.linspace(-98, -55, 40)
biny = np.arange(8, 32, np.diff(binx)[0])

for country_name in caribbean_countries:
    idx = np.where(imin0 == country2id[country_name])[0]

    # keep going if we have trajectory for this country
    if idx.size:
        fig = plt.figure(dpi=150)
        ax = fig.add_subplot(1,1,1,projection=ccrs.PlateCarree())

        # load a random set of trajectories
        x_c = np.empty((len(idx), 0))
        y_c = np.empty((len(idx), 0))

        # get all the trajectories for the different months
        for file in files:
            df = xr.open_dataset(file)
            x_c = np.hstack((x_c, df['lon'][idx]))
            y_c = np.hstack((y_c, df['lat'][idx]))

            # plot mean trajectory per month
            #x_mean = np.mean(df['lon'][idx], 0)
            #y_mean = np.mean(df['lat'][idx], 0)
            #ax.plot(x_mean, y_mean, linewidth=0.5);

            # plot n random trajectory
            #rand_id = np.random.randint(0, len(idx), 5)
            #ax.plot(x[idx[rand_id]].T, y[idx[rand_id]].T, linewidth=0.5);
            #ax.plot(x[idx[rand_id],:plot_days].T, y[idx[rand_id],:plot_days].T, linewidth=0.5);

            #ax.plot(x[idx,:plot_days].T, y[idx,:plot_days].T, linewidth=0.5);

        geo_map(ax)
        ax.add_geometries(caribbean_countries_geo[country_name], ccrs.PlateCarree(), facecolor='red', alpha=0.5)

        # binned the data
        ret = stats.binned_statistic_2d(x_c.flatten(), y_c.flatten(), None, 'count', bins=[binx, biny], expand_binnumbers=True)
        ret.statistic[ret.statistic == 0] = np.nan
        pc = ax.pcolormesh(binx, biny, ret.statistic.T, cmap=cmocean.cm.dense, transform=ccrs.PlateCarree())

        add_colorbar(fig, ax, pc, fmt=None, range_limit=None)
        ax.set_title('%s' % country_name)
        fig.savefig(output_folders + '%s.png' % country_name)
#%%

##

