#!/bin/bash
#SBATCH --job-name=calpuff_test
#SBATCH --output=/users/p2993/calpuff/calpuff_test.log

/users/p2993/bin/calpuff /users/p2993/calpuff/jelsava/point/annual/calpuff_8.inp

