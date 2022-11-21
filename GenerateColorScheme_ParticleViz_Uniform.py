import xarray as xr
import numpy as np
import os
from os.path import join
import pandas as pd
import json
import cmocean.cm as cmo
import matplotlib.pyplot as plt

# This program is an example to generate a json file that ParticleViz can use to display
##
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
    'Suriname']

countries_file = 'data/coasts_uniform.csv'
df = pd.read_csv(countries_file, header=0)
subsample_rate = 1

##
ids_by_particles = df['country id'].values
country_ids = df['country id'].unique()

countries = []

tot_countries = len(country_ids)
# colors = plt.cm.get_cmap('cmo.amp', tot_countries)
colors = plt.cm.get_cmap('hsv', tot_countries)

def single_release(tot_countries):
    # It assumes that the first particles start with id = 0
    prev_end = 0
    for c_id in range(1, tot_countries):
        start_id = prev_end
        # end_id = np.floor((np.where(ids_by_particles == country_ids[c_id])[0][0] - 1)/subsample_rate)
        end_id = np.where(ids_by_particles == country_ids[c_id])[0][0] - 1
        prev_end = end_id + 1
        countries.append({
            'name': caribbean_countries[c_id-1],
            "color": F"rgb{tuple(255*np.array(colors(c_id-1)))}",
            "index": F"{start_id}-{end_id}"
        })

    example_json = {
        "Countries": countries
    }

    with open("/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/Particle_viz/data/color_schemes/ColorSchemeCaribbeanUniform.json", 'w') as f:
        json.dump(example_json, f, indent=4)

    print("Done!")

def multiple_release(tot_countries,number_months, output_file):
    # It assumes that the first particles start with id = 0
    for c_month in range(number_months):
        print(f"Working with month {c_month}")
        prev_end = 0
        for c_id in range(tot_countries-1):
            start_id = prev_end
            end_id = np.where(ids_by_particles == country_ids[c_id+1])[0][0] - 1
            prev_end = end_id + 1
            if( len(countries) <= c_id):
                countries.append({
                    'name': caribbean_countries[c_id],
                    "color": F"rgb{tuple(255*np.array(colors(c_id)))}",
                    "index": ",".join([f"{i}" for i in range(start_id, end_id)])
                })
            else:
                countries[c_id]["index"] += ",".join([f"{i}" for i in range(start_id+len(ids_by_particles)*c_month, end_id+len(ids_by_particles)*c_month)])

    example_json = {
        "Countries": countries
    }

    with open(output_file, 'w') as f:
        json.dump(example_json, f, indent=4)

    print("Done!")

multiple_release(tot_countries, 12, "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/CARIBBEAN_MarineLitter/outputs/color_squeme_uniform_twelve_releases.json")
##


##

