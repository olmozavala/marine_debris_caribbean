from os.path import join
from netCDF4 import Dataset
import xarray as xr
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib import cm
import cmocean.cm as cmo
import matplotlib as mpl
from viz_utils.constants import PlotMode, BackgroundType
import os
from multiprocessing import Pool
import sys
sys.path.append("eoas_pyutils/")

from viz_utils.eoa_viz import EOAImageVisualizer

np.set_printoptions(precision=4)
resolution_txt = "one_tenth"  # In degrees


def make_plot(LONS, LATS, data, title, file_name):
    # IMPORTANT IT MAY LOOK WRONG ON PYCHARM BUT CORRECT ON THE PNG
    n_colors = 255  # NUmber of color sin the color bar
    fig, ax= plt.subplots(1, 1, figsize=(20,20), subplot_kw={'projection': ccrs.PlateCarree()})

    # norm = mpl.colors.LogNorm(vmin=1, vmax=max(10, int(np.nanmax(data))))
    norm = mpl.colors.LogNorm()
    cs = ax.contourf(LONS, LATS, data, levels=np.append([10**i for i in range(3)], [200000]), transform=ccrs.PlateCarree(), cmap=cmo.thermal, norm=norm)
    fig.colorbar(cs, shrink=.3)
    # cax.set_title(title)
    plt.savefig(file_name, bbox_inches='tight')
    # plt.show()
    plt.close()


def make_hist(input_folder, output_folder, input_file, grid_resolution, tot_proc=10, bbox=(-180,180,-90,90)):
    """
    It computes the histogram of a single file in parallel, using tot processors
    :return:
    """
    # Parameters. How many processors and what grid_resolution to create the histogram

    # Reads input folders
    file_name = join(input_folder, input_file)

    # Creates output folders and file names
    output_histogram_folder = join(output_folder, "histo")
    output_imgs_folder = join(output_folder, "images")
    output_tiff_folder = join(output_folder, "tiffs")

    if not(os.path.exists(output_histogram_folder)):
        os.makedirs(output_histogram_folder)
    if not(os.path.exists(output_imgs_folder)):
        os.makedirs(output_imgs_folder)
    if not(os.path.exists(output_tiff_folder)):
        os.makedirs(output_tiff_folder)

    output_file = join(output_histogram_folder, F"{input_file.replace('.nc','')}_histogram_{resolution_txt}")
    output_file_tiff = join(output_tiff_folder, F"{input_file.replace('.nc','')}_histogram_{resolution_txt}.tiff")

    # Creates the output data frame and creates the output grid
    print(F"Working with file: {file_name}")
    ds = Dataset(file_name, "r", format="NETCDF4")

    tot_lons = int( (bbox[1]-bbox[0])/grid_resolution)
    tot_lats = int( (bbox[3]-bbox[2])/grid_resolution)

    # lats and lons contain ALL the positions from the files
    lats = ds['lat'][:]
    lons = ds['lon'][:]
    tot_particles = len(lats)

    LATS = np.linspace(bbox[2], bbox[3], tot_lats+1)
    LONS = np.linspace(bbox[0], bbox[1], tot_lons+1)

    # Computes the histogram in parallel partitioning by locations (TODO it should be modified to compute by file)
    with Pool(tot_proc) as pool:
        acum_histo_par = pool.starmap(parallelSum, [(lats, lons, LATS, LONS, i, tot_proc) for i in range(tot_proc)])

    acum_histo_par = np.array(acum_histo_par)
    acum_histo = np.sum(acum_histo_par, axis=0)
    # For debugging
    # acum_histo = parallelSum(lats, lons, LATS, LONS, 0, 1)

    # REVIEW THIS PART!!! THE 12 IS BECAUSE WE ASSUME 12 RELEASES PER YEAR
    tons_per_particle = ((6.5e6)/(tot_particles * 12))
    acum_histo = tons_per_particle*acum_histo + 1
    idx = acum_histo == 1
    acum_histo[idx] = np.nan
    # Avoid zeros
    idx = acum_histo <= 0
    acum_histo[idx] = 1
    # Saving accumulated histogram as netcdf
    print("Saving files....")
    ds = xr.Dataset({"histo": (("lat", "lon"), acum_histo)}, {"lat": LATS, "lon": LONS})
    ds = addAttributes(ds)
    ds.to_netcdf(F"{output_file}.nc")
    ds.close()

    make_plot(LONS, LATS, acum_histo, F"Acumulated  {input_file}", join(output_imgs_folder, F"{input_file.replace('.nc','')}_Accumulated.png"))
    # os.system(F"gdal_translate -a_srs EPSG:4326 NETCDF:{output_file}.nc:histo {output_file_tiff}")
    os.system(F"gdal_translate  NETCDF:{output_file}.nc:histo {output_file_tiff}")


def parallelSum(lats, lons, LATS, LONS, id_proc, tot_proc):
    """
    Depending on the assigned id proc it will sum its corresponding lats and lons into the grid
    :param lats:
    :param lons:
    :param LATS:
    :param LONS:
    :param id_proc:
    :param tot_proc:
    :return:
    """

    # makes the grid and flattens the arrays
    tot_lats = len(LATS)
    tot_lons = len(LONS)
    histo = np.zeros((tot_lats, tot_lons))
    c_lats = lats.flatten()
    c_lons = lons.flatten()
    tot_particles = len(c_lats)

    segment_size = int(np.ceil(tot_particles/tot_proc))
    seg_from = int(segment_size*id_proc)
    seg_to = int(np.min((segment_size*(id_proc+1), tot_particles)))
    print(F"Id: {id_proc}, tot_proc: {tot_proc}, tot particles: {tot_particles} from: {seg_from} to: {seg_to}")

    # Iterate over all particles. It searches the index in the GRID for each particle and adds it into the position
    lats_pos = np.searchsorted(LATS, c_lats[seg_from:seg_to])
    lons_pos = np.searchsorted(LONS, c_lons[seg_from:seg_to])

    lats_pos -= 1 # Fixing the indexing
    lons_pos -= 1 # Fixing the indexing
    for i in range(len(lats_pos)):
        histo[lats_pos[i], lons_pos[i]] += 1

    return histo


def addAttributes(ds):
    """Adds default attributes the the netcdf to make it CF-Compliant"""
    ds.attrs['Conventions'] = "CF-1.0"
    ds['lat'].attrs['standard_name'] = "latitude"
    ds['lat'].attrs['long_name'] = "latitude"
    ds['lat'].attrs['units'] = "degrees_north"
    ds['lat'].attrs['axis'] = "Y"
    ds['lon'].attrs['standard_name'] = "longitude"
    ds['lon'].attrs['long_name'] = "longitude"
    ds['lon'].attrs['units'] = "degrees_east"
    ds['lon'].attrs['axis'] = "X"
    return ds


def mergeFiles(input_folder, output_folder, start_year=10, end_year=21):
    total_days = (365 * (end_year-start_year)) - (11 * (6 * 30))# How many time steps were evaluated in TOTAL by all the model
    bbox = (-98.5, -51.6, 3.9, 31)

    print("Merging files....")
    first_file = True
    lat = 0
    lon = 0
    viz_obj = False
    for y in range(start_year, end_year):
        for m in range(1, 13):
            input_file = F"cm_uniform_20{y:02d}-{m:02d}-01_histogram_{resolution_txt}.nc"
            print(F"Adding file {input_file}")

            file_name = join(input_folder, "histo", input_file)
            ds = Dataset(file_name, "r", format="NETCDF4")

            if first_file:
                lat = ds['lat'][:]
                lon = ds['lon'][:]
                c_histo = np.full_like(ds['histo'][:], 0)
                first_file = False

                viz_obj = EOAImageVisualizer(disp_images=False, lons=lon, lats=lat,
                                             output_folder=join(output_folder, 'images'),
                                             background=BackgroundType.BLUE_MARBLE_HR,
                                             norm=mpl.colors.LogNorm(vmin=1, vmax=10 ** 10, clip=True),
                                             figsize=20)
            else:
                no_nan = ~np.isnan(ds['histo'][:].data)
                c_histo[no_nan] += ds['histo'][:].data[no_nan]
            ds.close()

            # ------------- Debugging ----------
            viz_obj.plot_2d_data_np(c_histo, ['histo'], cmap='cmo.amp', title=F'Histogram 2010-01 to 20{y:02d}-{m:02d}', file_name_prefix=F"20{y:02d}-{m:02d}")

    # f_histo = c_histo/total_days
    f_histo = c_histo
    print(F"Saving merged file.... min value: {np.amin(f_histo)} max value: {np.amax(f_histo)}")
    # ds = xr.Dataset({"histo": (("lat", "lon"), f_histo)}, {"lat": lat, "lon": lon})
    ds = xr.Dataset({"histo": (("lat", "lon"), c_histo)}, {"lat": lat, "lon": lon})
    ds = addAttributes(ds)
    ds['histo'].attrs['standard_name'] = "Histogram"
    output_file = join(output_folder,F"Merged.nc")
    output_file_tiff = join(output_folder,F"Merged.tiff")
    ds.to_netcdf(output_file)
    ds.close()
    os.system(F"gdal_translate  NETCDF:{output_file}:histo {output_file_tiff}")
    print("Done!")


def dispMerged(output_folder):
    file_name = join(output_folder, "Merged.nc")
    ds = xr.open_dataset(file_name)
    lats = ds.lat
    lons = ds.lon
    histo = ds.histo

    viz_obj = EOAImageVisualizer(disp_images=True, lons=lons, lats=lats, output_folder=output_folder,
                                 background=BackgroundType.BLUE_MARBLE_HR,
                                 norm=mpl.colors.LogNorm(vmin=10**5, vmax=10**12, clip=True),
                                 figsize=20)
    # viz_obj.plot_2d_data_np(histo, ['histo'], cmap='cmo.amp', title='Histogram 2010-2021', file_name_prefix="Histogram")
    output_folder_imgs = join(output_folder,"images")
    viz_obj.make_video_from_images(output_folder_imgs, join(output_folder,"video.mp4"), fps=2)


if __name__ == "__main__":
    # input_folder = "/data/CaribbeanMarineDebris/output/cm_uniform"
    output_folder = "/data/CaribbeanMarineDebris/output"
    input_folder = "/nexsan/people/pmiron/projects_mars/caribbean-marine-litter/data/output/cm_uniform"
    # output_folder = "/data/CaribbeanMarineDebris/output"

    grid_resolution = 1/10  # Degrees
    tot_proc = 10

    start_year = 21
    end_year = 22
    # =========================== Makes histogram =====================
    # # This part is to generate (in a loop) CF-netcdf files of the accumulated locations.
    # bbox = (-98.5, -51.6, 3.9, 31)
    # for y in range(start_year, end_year):
    #     for m in range(10, 13):
    #         # I modify it so that it takes the names from heere NOT from the config file
    #         file_name = F"cm_uniform_20{y:02d}-{m:02d}-01.nc"
    #         make_hist(input_folder, output_folder, file_name, grid_resolution, tot_proc, bbox)

    # =========================== Merges histograms =====================
    start_year = 10
    end_year = 22
    # Here we can merge those files into a single one
    input_folder = "/Net/work/ozavala/CARIBBEAN_marine_debris/CODE/output"
    output_folder = "/data/CaribbeanMarineDebris/output"
    # mergeFiles(input_folder, output_folder, start_year=start_year, end_year=end_year)

    # =========================== Display Merged =====================
    dispMerged(output_folder)