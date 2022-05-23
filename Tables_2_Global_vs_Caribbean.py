from os.path import join
import matplotlib.pyplot as plt
import time
import json
import plotly.graph_objs as go
import numpy as np
import plotly.graph_objects as go
import os
import subprocess
import shutil
import pandas as pd

MAX_ROWS = 15
skip_countries = []
data = {}
global_year = 0


def makePDF(input_folder):
    # Copy script
    print(F"Making pdf inside {input_folder}....")
    sh_file = "pngTopdf.sh"
    if not os.path.exists(join(input_folder, sh_file)):
        shutil.copyfile(sh_file, join(input_folder,sh_file))
    # Run it
    p = subprocess.Popen(["sh", join(input_folder,sh_file)], cwd=input_folder)
    p.wait()
    print("Done!")

def read_data(c_data):
    country_from_data = {}  # Data from for each country

    if 'from' in c_data.keys():
        for c_from in c_data['from']['from']:
            if c_from['name'] not in country_from_data:
                country_from_data[c_from['name']] = 0  # Initialize with zero for this country all years
            country_from_data[c_from['name']] = c_from['perc']
    else:
        country_from_data = {}
        # Iterate over all the years data for this country

    country_to_data = {}
    if 'to' in c_data.keys():
        for c_to in c_data['to']['to']:
            if c_to['name'] not in country_to_data:
                country_to_data[c_to['name']] = 0  # Initialize with zero for this country all years

            country_to_data[c_to['name']] = c_to['perc']
    else:
        country_from_data = {}
    return  country_from_data, country_to_data

def make_bar_plot(df, title, ax):
    show_n_countries = 10
    # df = df.sort_values(ascending=False)
    df = df.head(show_n_countries)
    connected_countries = df.index
    tot_countries = len(connected_countries)
    df.plot.bar(ax=ax)
    # country_from_data has all the data for all the years. In each 'inside country' it has an array of values, one per year
    # connected_countries = df.index
    # tot_countries = len(connected_countries)
    # pos = np.arange(tot_countries)
    # ax.bar(pos, df.values)
    # ax.set_xticks(pos, labels=connected_countries)
    ax.set_title(title)
    ax.set_ylabel("Percentage of MPW")
    ax.tick_params(labelrotation=30)

def make_plots(car_data, glob_data, output_folder, plot_type="Bar"):

    # Here we assume all years have the same countries
    all_countries = car_data.keys()
    # Iterate over all the countries

    for c_country in all_countries:
        try:
            print(F"Working with country: {c_country}...")

            car_from_data, car_to_data = read_data(car_data[c_country])
            glob_from_data, glob_to_data = read_data(glob_data[c_country])

            ## -------------------------------------
            # ----- Making the plots -------------------

            # ----- From part -------------------
            if plot_type == "Bar":
                fig, axs = plt.subplots(1, 2, figsize=(15, 5))
                if len(car_from_data) > 0:
                    from_dict = {'Caribbean': car_from_data, 'Global': glob_from_data}
                    df = pd.DataFrame(from_dict)
                    make_bar_plot(df, F"Caribbean vs Global From {c_country}", axs[0])
                # ----- To part -------------------
                if len(car_to_data) > 0:
                    to_dict = {'Caribbean': car_to_data, 'Global': glob_to_data}
                    df = pd.DataFrame(to_dict)
                    make_bar_plot(df, F"Caribbean vs Global To {c_country}", axs[1])

            plt.tight_layout()
            plt.savefig(join(output_folder,F"{c_country}.png"))
            # plt.show()
            plt.close()
        except Exception as e:
            print(F"Failed for {c_country}: {e}")

if __name__ == '__main__':

    # ---------------- Multiple years ---------------
    car_folder = "/data/COAPS_Net/work/ozavala/CARIBBEAN_marine_debris/statistics/FromCaribbean/json/2021"
    glob_folder = "/data/COAPS_Net/work/ozavala/CARIBBEAN_marine_debris/statistics/FromGlobal"
    output_folder = "/data/COAPS_Net/work/ozavala/CARIBBEAN_marine_debris/statistics/CaribbeanVsGlobal"

    car_input_file = join(car_folder, 'ReachedTablesData.json')
    glob_input_file = join(glob_folder, 'ReachedTablesData.json')

    with open(car_input_file) as f:
        car_data = json.load(f)
    with open(glob_input_file) as f:
        glob_data = json.load(f)

    imgs_output_folder = join(output_folder, "imgs")
    pdf_output_folder = join(output_folder, "pdf")
    if not os.path.exists(imgs_output_folder):
        os.makedirs(imgs_output_folder)
    if not os.path.exists(pdf_output_folder):
        os.makedirs(pdf_output_folder)

    # make_plots(car_data, glob_data, imgs_output_folder)
    makePDF(imgs_output_folder)

    # Wait for the PDFs to be created.
    print("Waiting to create pdf....")
    time.sleep(10)
    input_file = join(imgs_output_folder,  F"ReachedTablesDataCaribbean.pdf")
    shutil.copyfile(input_file , F"{join(pdf_output_folder, F'ReachedTablesData.pdf')}")
    print(F"Saved to {output_file}")
    print("Done!")