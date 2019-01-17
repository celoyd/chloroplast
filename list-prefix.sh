#!/bin/bash

set -eu

sat=$1
frame=$2
band=$(printf "%02d" $((10#$3)))
year=$4
doy=$(printf "%03d" $((10#$5)))
hour=$6
minute=$7

dir="ABI-L1b-Rad$frame/$year/$doy/$hour/"
if [ "$frame" == "M" ]; then
    frame=M1
fi
filename="OR_ABI-L1b-Rad$frame-M3C${band}_${sat}_s$year$doy$hour$minute"

prefix="$dir$filename"

(>&2 echo "Checking for $prefix")

if [ "$sat" = "G16" ]; then
    longsat=goes16
else
    longsat=goes17
fi

list=`aws s3api list-objects --bucket noaa-${longsat} --prefix="$prefix" | jq -r '.Contents[].Key'`

if [ -z $list ]; then
  exit 1
else
  echo $list
fi
