from config.MainConfig import get_config
from config.params import GlobalModel
from proj_io.common_io import load_obj
from os.path import join
import numpy as np
import os
import xarray as xr
from calendar import monthrange
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

config = get_config()

output_folder = config[GlobalModel.caribbean_from_global_folder]

def debrisDecay(N, t, decay_time=5):
    '''
    Debris decay in years
    :param N:
    :param t:
    :param decay_time: Decay time in years
    :return:
    '''
    y = N*np.exp(-t/decay_time)
    return y


def get_amount_particles(decay_scenarios=[5]):
    '''
    Obtains the amount of particles with and without decay scenarios
    :param decay_scenarios:
    :return:
    '''
    years = np.arange(2010,2020)
    tot_part = np.zeros(len(years)*365 + 2)
    tot_part_w_decay = np.zeros((len(decay_scenarios), len(years)*365 + 2))
    dates = np.arange(datetime(years[0],1,1), datetime(years[-1]+1,1,1), timedelta(days=1)).astype(datetime)
    c_idx = 0
    for year in years[0:10]:
        print(F"Reading year: {year}")
        for month in range(1, 13):
            file_name = join(output_folder,F"{year}_{month}.pkl")
            cf = load_obj(file_name)
            num_days = monthrange(year, month)[1] # num_days = 28
            tot_part[c_idx:c_idx+num_days] = [len(x['lat']) for x in cf.values()]
            counts_per_release = [x['count_per_release'] for x in cf.values()]
            for i, c_decay_time in enumerate(decay_scenarios):
                # tot = [x for i,x in enumerate(counts_per_release)]  # Just for debuggin the computation of decay
                if c_idx == 0:
                    new_values = [debrisDecay(counts_per_day, day/365, decay_time=c_decay_time) for day, counts_per_day in enumerate(counts_per_release)]
                else:
                    new_values = [np.sum(debrisDecay(np.array(counts_per_day), (np.arange(len(counts_per_day))*31 + day)/365, decay_time=c_decay_time)) for day, counts_per_day in enumerate(counts_per_release)]
                tot_part_w_decay[i, c_idx:c_idx+num_days] = new_values
            c_idx += num_days

    return tot_part, tot_part_w_decay, dates

if __name__ == "__main__":
    decay_scenarios = [5,10,20]
    tot_part, tot_part_w_decay, dates = get_amount_particles(decay_scenarios)

    plt.plot(dates, tot_part, label='Without decay')
    for i, c_decay_time in enumerate(decay_scenarios):
        plt.plot(dates, tot_part_w_decay[i], label=F'{c_decay_time} years decay')
    plt.ylabel("Number of particles")
    plt.title("Amount of particles inside the Caribbean region, by decay function")
    plt.legend()
    plt.show()

    # Test decay
    # N = 1000
    # t0 = 5 # years to decay
    # t = np.linspace(0, 5, 365*5)
    # y = debrisDecay(N, t, t0)
    # plt.plot(t,y)
    # plt.show()
