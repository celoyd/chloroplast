#!/bin/bash

set -eux

sat=$1
year=$2
doy=$(printf "%03d" $((10#$3)))
hour=$4
minute=$5
dst_path="whole_$6"
clean_path=$6

./rgb_frame.sh $sat C $year $doy $hour $minute $dst_path

# https://www.gdal.org/structGDALWarpOptions.html

gdalwarp -wo SOURCE_EXTRA=64 -wo SAMPLE_STEPS=128 -wo CUTLINE_ALL_TOUCHED=TRUE -et 0 -r bilinear -cutline westcoast.json -crop_to_cutline -t_srs EPSG:3310 -tr 1000 1000 $dst_path "untrimmed_${dst_path}"

gdalwarp -wo SOURCE_EXTRA=64 -wo SAMPLE_STEPS=128 -wo CUTLINE_ALL_TOUCHED=TRUE -et 0 -r bilinear -cutline westcoast.json "untrimmed_${dst_path}" $clean_path

# rm "untrimmed_${dst_path}" $dst_path
