#!/bin/bash

dst=${2:-.}

if [ ! -f $dst ]; then
    aws s3 cp s3://noaa-goes16/$1 $dst
fi