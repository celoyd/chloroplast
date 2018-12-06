#!/usr/bin/env python3

import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description='Output time of last GOES frame')
parser.add_argument('--conus', action="store_true",
                    help='Output time of last continental US frame')
parser.add_argument('--fulldisk', action="store_true",
                    help='Output time of last full disk frame')

args = parser.parse_args()

now = datetime.utcnow()
year = now.year
day_of_year = now.timetuple().tm_yday
hour = now.hour
minute = now.minute

if args.fulldisk:
    minute = int(round(float(minute)/15)*15)

if args.conus:
    minute = int(round(float(minute)/5)*5)-3

print(f"{year} {day_of_year} {hour} {minute}")
