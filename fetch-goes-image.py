#!/usr/bin/env python3

import argparse
import os
import sys

from datetime import datetime

import boto3

from nctogtiff import nctogtiff

class FetchGOES(object):
    def parse_arguments(self):
        self.parser = argparse.ArgumentParser(description='Output time of last GOES frame')
        # TODO limit to F, C, M
        self.parser.add_argument('frame', help='Type of frame to fetch: F, C, M')
        self.parser.add_argument('date', nargs=argparse.REMAINDER,
                                  help='Date, in format year day_of_year hour day')

        # add 'leave_downloads' argument?
        # add verbosity flag

        self.parser.parse_args(namespace=self)

        if self.date:
            (self.year, self.doy, self.hour, self.minute) = [int(v) for v in self.date]
            print("Set date from command line arguments")

    def get_last_frame_time(self):
        """ Gets the time of the last frame of a given type
        """
        now = datetime.utcnow()

        self.year = now.year
        self.doy = now.timetuple().tm_yday
        self.hour = now.hour
        self.minute = now.minute

        if self.frame == "F":
            self.minute = 15*(self.minute // 15)

        if self.frame == "C":
            # TODO do this better
            self.minute = int(round(float(self.minute)/5)*5)-3

        print("Date set automatically")

    def get_s3_bucket(self, satellite="goes17"):
        self.s3 = boto3.resource('s3') 

        self.bucket_name = f"noaa-{satellite}"
        bucket = self.s3.Bucket(self.bucket_name)
        return bucket

    def list_prefix(self, bucket, band):
        directory = f"ABI-L1b-Rad{self.frame}/{self.year}/{self.doy:03}/{self.hour:02}/"
        filename = f"OR_ABI-L1b-Rad{self.frame}-M3C{band:02}_G17_s{self.year}{self.doy:03}{self.hour:02}{self.minute:02}"
        prefix = directory+filename

        print(f"Checking for {prefix}")

        files = bucket.objects.filter(Prefix=prefix)
    
        output = [key.key for key in files]
        if not len(output):
            raise Exception("FIle not found in bucket for frame and band")

        for file in output:
            print(file)
        return output[0]

    def get_file(self, filename, channel):
        start_time = f"{self.year}{self.doy:03}{self.hour:02}{self.minute:02}"
        dest = f"{start_time}.{channel}.nc"

        if not os.path.exists(dest) and os.path.isfile(dest):
            object = self.s3.Object(self.bucket_name, filename).download_file(dest)

    def toa(self):
        #granule=$(basename $1 .nc)
        #python nctogtiff.py $1 $granule.toa.tif && rm $1
        

if __name__ == '__main__':
    g = FetchGOES()
    g.parse_arguments()
    if not g.date:
        g.get_last_frame_time()

    bucket = g.get_s3_bucket()
    bands = {
        1: 'blu',
        2: 'red',
        3: 'nir',
    }

    for band in bands.keys():
        remote_file = g.list_prefix(bucket, band)
        g.get_file(remote_file, bands[band])

    for band in band.values():
        # TODO this should be parallelised
        source = f"{start_time}.{band}.nc"
        dest = f"{start_time}.{band}.toa.tif"
        nctogtiff(source, dest)

        # TODO parallel -j3
        # TODO convert to Python
        warped = f"{start_time}.{band}.toa.resized.tif"
        command = f"gdalwarp -wm 1000 -r average -tr 1002.0086577437706 1002.0086577437706 {dest} {warped}"
        subprocess.run(command)


