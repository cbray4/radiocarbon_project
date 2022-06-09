#!/bin/bash

#SBATCH --account=arcc-students
#SBATCH --time=00:00:10
#SBATCH --output=iterateOutput.txt
#SBATCH --error=iterateErrors.txt

python iterateTest.py