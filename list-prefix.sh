#!/bin/bash

set -eu

frame=$1
band=$(printf "%02d" $((10#$2)))
year=$3
doy=$(printf "%03d" $((10#$4)))
hour=$5
minute=$6

dir="ABI-L1b-Rad$frame/$year/$doy/$hour/"
if [ "$frame" == "M" ]; then
    frame=M1
fi
filename="OR_ABI-L1b-Rad$frame-M3C${band}_G16_s$year$doy$hour$minute"

prefix="$dir$filename"

(>&2 echo "Checking for $prefix")

list=`aws s3api list-objects --bucket noaa-goes16 --prefix="$prefix" | jq -r '.Contents[].Key'`

if [ -z $list ]; then
  exit 1
else
  echo $list
fi
