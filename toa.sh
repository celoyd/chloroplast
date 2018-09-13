#!/bin/bash

set -eux

granule=$(basename $1 .nc)

python nctogtiff.py $1 $granule.toa.tif && rm $1

#echo "Wrote to $granule.toa.tif"
