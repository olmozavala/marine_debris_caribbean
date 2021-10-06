"""
Usage:
  GlobalModel.py <start_date> <end_date> <winds> <diffusion> <unbeaching> <name> <days_per_batch>
  GlobalModel.py <start_date> <end_date> <winds> <diffusion> <unbeaching> <name> <restart_file> <days_per_batch>
  GlobalModel.py single <start_date> <end_date> <winds> <diffusion> <unbeaching> <name>
  GlobalModel.py (-h | --help)
  GlobalModel.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  <winds>       Something [default: 3]
"""
from docopt import docopt
from parcels.scripts import *
from datetime import timedelta, datetime
from os.path import join
from config.params import GlobalModel
from config.MainConfig import get_config
import sys
import os
from models.GlobalModel import sequential
from distutils.util import strtobool
from proj_utils.several_utils import get_file_name, str2bool
# from models.models import sequential

try:
    from mpi4py import MPI
except:
    MPI = None

time_format = "%Y-%m-%d:%H"
time_format_red = "%Y_%m_%d"

def runWithRestart(days_per_batch, config, start_date, end_date, winds, diffusion, unbeaching, name, restart_file=''):
    part_n = 0
    # =================== Computing all the models in 'batches' =====================

    cur_end_date = min(start_date + timedelta(days=days_per_batch), end_date)
    cur_name = get_file_name(name, start_date, cur_end_date, part_n)
    print(F"{start_date.strftime(time_format)} {cur_end_date.strftime(time_format)} winds={winds} diff={diffusion} " \
          F"unbeaching={unbeaching} name={cur_name}")

    if (restart_file != '') and (os.path.exists(restart_file)):
        sequential(start_date, cur_end_date, config, cur_name, winds=winds, unbeaching=unbeaching, diffusion=diffusion,
                   restart_file=restart_file)
    else:
        # --------- First run without restart file ----------
        sequential(start_date, cur_end_date, config, cur_name, winds=winds, unbeaching=unbeaching, diffusion=diffusion)

    if MPI:
        print(F"----- Waiting for all the processors to finish.....", flush=True)
        MPI.COMM_WORLD.Barrier()

    # # --------- Iterate over all the rest of the models, specify the restart file in each case
    while(cur_end_date < end_date):
        prev_start_date = start_date
        prev_end_date = cur_end_date
        start_date = cur_end_date # We need to add one or we will repeat a day
        cur_end_date = min(start_date + timedelta(days=days_per_batch), end_date)
        # Define the restart file to use (previous output file)
        restart_file = join(config[GlobalModel.output_folder], F"{get_file_name(name, prev_start_date, prev_end_date, part_n)}.nc")

        print(F" ================================================================================= ")
        print(F" ================================================================================= ")
        print(F" ================================================================================= ")

        # Define the new output file name
        part_n += 1
        cur_name = get_file_name(name, start_date, cur_end_date, part_n)
        print(F"{start_date.strftime(time_format)} {cur_end_date.strftime(time_format)} winds={winds} diff={diffusion} " \
          F"unbeaching={unbeaching} name={cur_name}")
        sequential(start_date, cur_end_date, config, cur_name, winds=winds, unbeaching=unbeaching, diffusion=diffusion, restart_file=restart_file)

        # =================== Here we merge all the output files into one ===========================
        if MPI:
            print(F"----Waiting for file to be saved proc {MPI.COMM_WORLD.Get_rank()} ... -------------", flush=True)
            MPI.COMM_WORLD.Barrier()
            print("Done!", flush=True)

if __name__ == "__main__":
    # Some run examples:
    # GlobalModel.py 2010-01-01:0 2010-03-11:0 True False False TEST 10 //Without restart
    # GlobalModel.py 2010-01-21:0 2010-01-31:0 True False False TEST /home/data/UN_Litter_data/output/TEST_2010-01-21_2010-01-31.nc 10  //With restart
    # Parallel run examples with mpirun:
    # mpirun -np 8 python GlobalModel.py 2010-01-01:0 2010-03-11:0 True False False TEST 10 //Without restart
    args = docopt(__doc__, version='OZ Example 0.1')
    # print(args)
    start_date = datetime.strptime(args['<start_date>'], "%Y-%m-%d:%H")
    end_date = datetime.strptime(args['<end_date>'], "%Y-%m-%d:%H")
    winds = bool(strtobool(args['<winds>']))
    diffusion = bool(strtobool(args['<diffusion>']))
    unbeaching = bool(strtobool(args['<unbeaching>']))
    name = args['<name>']
    restart_file = args['<restart_file>']
    single = args['single']
    print(F"Name: {name}")
    print(F"Start date: {start_date} End date: {end_date} winds={winds} diffusion={diffusion} unbeaching={unbeaching}")
    if single:
        # Running without restart file
        print("Continuous run!!!!!")
        # sequential(start_date, end_date, config, name, winds=winds, unbeaching=unbeaching, diffusion=diffusion)
    else:
        days_per_batch = int(args['<days_per_batch>'])
        config = get_config()
        if restart_file:
            if os.path.exists(restart_file):
                print(F"Batches run from restart ({days_per_batch})!!!!!  {restart_file} ")
                runWithRestart(days_per_batch, config, start_date, end_date, winds, diffusion, unbeaching, name, restart_file=restart_file)
            else:
                print(F"Error: the specified restart file {restart_file} doesn't exist!")
        else:
            print("Batches run without restart !!!!!")
            runWithRestart(days_per_batch, config, start_date, end_date, winds, diffusion, unbeaching, name)