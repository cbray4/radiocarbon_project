#!/bin/bash

#SBATCH --account=arcc-students
#SBATCH --time=00:00:10
#SBATCH --output=/project/arcc-students/cbray3/radiocarbon_text/raw_output/card_output.txt
#SBATCH --error=/project/arcc-students/cbray3/radiocarbon_text/raw_output/card_errors.txt

python /project/arcc-students/cbray3/radiocarbon_code/multicard_read.py
