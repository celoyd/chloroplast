#!/bin/bash

dst=${2:-.}

if `echo $1 | grep -q _G16_s`; then
    longsat=goes16
else
    longsat=goes17
fi

fullpath="s3://noaa-${longsat}/$1"
echo $fullpath

if [ ! -f $dst ]; then
    aws s3 cp $fullpath $dst
fi