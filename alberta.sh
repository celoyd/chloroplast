#!/bin/bash

set -eux

year=$1
doy=$(printf "%03d" $((10#$2)))
hour=$3
minute=$4
dst_path="whole_$5"
clean_path=$5

./rgb_frame.sh C $year $doy $hour $minute $dst_path

# What's the thing to make the edge not jagged again?
gdalwarp -wo SAMPLE_STEPS=100 -cblend 4 -et 0 -r bilinear -cutline westcoast.json -crop_to_cutline -t_srs EPSG:3310 -tr 1000 1000 $dst_path "untrimmed_${dst_path}"

gdalwarp -et 0.1 -cutline westcoast.json "untrimmed_${dst_path}" $clean_path

rm "untrimmed_${dst_path}" $dst_path
