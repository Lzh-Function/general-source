#!/bin/bash

source /opt/pip-env/bin/activate

python3 $(dirname $0)/cas2smi2sdf.py \
    --df_path
    --csv_dir_path
    --name 
    --sdf_dir_path 
    --url 
