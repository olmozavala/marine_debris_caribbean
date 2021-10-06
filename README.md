# Installation

## Anaconda
Create your conda environment from the file `geoeoas.yml`
```
conda env create -f yourfile.yml
```

Activate your environment: `conda activate geoeoas`

# Run
## 0_Crop_Global_Data.py
It crops all the outputs of the Global model into a specified region

## 1_Analyze_data.ipynp
Notebook to display dynamic outputs of the regional from global data.

## GlobalModel.py
This code is the one in charge of running the global model. 
It can be executed in parallel and it splits the run in batches
to improve the performance.
```
GlobalModel.py 2010-01-01:0 2010-03-11:0 True False False TEST 10 
GlobalModel.py 2010-01-21:0 2010-01-31:0 True False False TEST restart_file.nc 
```
