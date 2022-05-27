#!/bin/bash

#SBATCH --account=arcc-students
#SBATCH --time=00:00:10
#SBATCH --output=/project/arcc-students/cbray3/radiocarbon_text/organized_output/organized_output.txt
#SBATCH --error=/project/arcc-students/cbray3/radiocarbon_text/organized_output/organized_errors.txt

python /project/arcc-students/cbray3/radiocarbon_code/test_organize_text.py