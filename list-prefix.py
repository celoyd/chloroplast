#!/usr/bin/env python3

import argparse
import os
import sys

from datetime import datetime

import boto3

parser = argparse.ArgumentParser(description='Check s3 for file')
parser.add_argument('frame', help='Frame type (F, C, M)')
parser.add_argument('band', help='Band (1, 2, 3)')
parser.add_argument('year', help='Year')
parser.add_argument('doy', help='Day of year (UTC)')
parser.add_argument('hour', help='Hour (UTC)')
parser.add_argument('minute', help='Minute')

args = parser.parse_args()

directory = f"ABI-L1b-Rad{args.frame}/{args.year}/{args.doy}/{args.hour}/"
filename = f"OR_ABI-L1b-Rad{args.frame}-M3C0{args.band}_G17_s{args.year}{args.doy}{args.hour}{args.minute}"
prefix = directory+filename

print(f"Checking for {prefix}")

s3 = boto3.resource('s3') 
goes_bucket = s3.Bucket('noaa-goes17')
files = goes_bucket.objects.filter(Prefix=prefix)

output = [key.key for key in files]
if not output:
    sys.exit(1)

for key in output:
    print(key)
