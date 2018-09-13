#!/bin/bash

set -eux

frame=$1
#band=$(printf "%02d" $2)
year=$2
doy=$(printf "%03d" $((10#$3)))
hour=$4
minute=$5
dst_path=$6

start_time="$year$doy$hour$minute"

blu=`./list-prefix.sh $frame 1 $year $doy $hour $minute`
red=`./list-prefix.sh $frame 2 $year $doy $hour $minute`
nir=`./list-prefix.sh $frame 3 $year $doy $hour $minute`

./get.sh $blu $start_time.blu.nc
./get.sh $red $start_time.red.nc
./get.sh $nir $start_time.nir.nc

parallel -j1 ./toa.sh $start_time.{}.nc ::: blu red nir

parallel -j3 gdalwarp -wm 1000 -r average -tr 1002.0086577437706 1002.0086577437706 $start_time.{}.toa.tif $start_time.{}.toa.resized.tif ::: blu red nir

parallel mv $start_time.{}.toa.resized.tif $start_time.{}.toa.tif ::: blu red nir

python weight.py $start_time.nir.toa.tif 1:3 $start_time.red.toa.tif $start_time.nr.tif

python weight.py $start_time.nr.tif 4:8 $start_time.blu.toa.tif $start_time.grn.tif

rio stack --overwrite --rgb --co compress=lzw $start_time.red.toa.tif $start_time.grn.tif $start_time.blu.toa.tif $start_time.rgb.tif

# blehhh
convert -gamma 1.5 -sigmoidal-contrast 10,10% -modulate 100,150 -channel B -gamma 0.55 -channel G -gamma 0.7 +channel -gamma 0.7 $start_time.rgb.tif $dst_path

rio edit-info $dst_path --like $start_time.blu.toa.tif --crs like --transform like --nodata 0

rm $start_time.red.toa.tif $start_time.blu.toa.tif $start_time.nr.tif $start_time.nir.toa.tif $start_time.grn.tif
