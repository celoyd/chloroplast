#!/usr/bin/env python3

import os, sys

from datetime import datetime

import boto3

frame = 'F'
band = 1

now = datetime.utcnow()
year = now.year
doy = now.timetuple().tm_yday
hour = now.hour
minute = 0

directory = f"ABI-L1b-Rad{frame}/{year}/{doy}/{hour}/"
filename = f"OR_ABI-L1b-Rad{frame}-M3C0{band}_G17_s{year}{doy}{hour}{minute}"
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
