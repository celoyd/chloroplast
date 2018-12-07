#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

from datetime import datetime

import boto3

from nctogtiff import nctogtiff
from weight import preprocess

class FetchGOES(object):
    BANDS = {
        1: 'blu',
        2: 'red',
        3: 'nir',
    }

    def process(self):
        self.parse_arguments()
        if not self.date:
            self.get_last_frame_time()

        start_time = f"{self.year}{self.doy:03}{self.hour:02}{self.minute:02}"

        bucket = self.get_s3_bucket()

        for band in self.BANDS.keys():
            remote_file = self.list_prefix(bucket, band)
            self.get_file(remote_file, self.BANDS[band])

        cwd = os.path.dirname(os.path.realpath(__file__))

        for band in self.BANDS.values():
            # TODO this should be parallelised
            source = f"{start_time}.{band}.nc"
            intermediate = f"{start_time}.{band}.toa.tif"
            if self.file_missing(intermediate):
                print(f"Converting .nc to .tif for {band}")
                nctogtiff(source, intermediate)
            # if not self.keep # keep intermediates
            # os.remove(source)

            # TODO parallel -j3
            # TODO convert to Python
            warped = f"{start_time}.{band}.toa.resized.tif"
            command = ["gdalwarp", "-wm", "1000", "-r", "average", "-tr", "1002.0086577437706",
                    "1002.0086577437706", intermediate, warped]
            if self.file_missing(warped):
                print(f"Converting .tif to .resized.tif for {band}")
                subprocess.run(command, cwd=cwd)
            # os.remove(intermediate)

        # weight
        (blu, red, nir) = [f"{start_time}.{band}.toa.resized.tif" for band in self.BANDS.values()]
        nr = f"{start_time}.nr.tif"
        grn = f"{start_time}.nr.tif"
        rgb = f"{start_time}.rgb.tif"
        out = f"{start_time}.tif"       # _or_ self.output

        if self.file_missing(nr):
            print(f"Composing nir, red to nr")
            preprocess(nir, red, nr, '1:3')
        if self.file_missing(grn):
            print(f"Composing nr, blu to grn")
            preprocess(nr, blu, grn, '4:8')

        # TODO convert to rasterio API calls
        command = ['rio', 'stack', '--overwrite', '--rgb', '--co',
                   'compress=lzw', red, grn, blu, rgb]
        if self.file_missing(rgb):
            print(f"Stacking bands")
            subprocess.run(command, cwd=cwd)

        # TODO replace convert with rio (?)
        command = ['convert', '-gamma', '1.5', '-sigmoidal-contrast', '10,10%',
                   '-modulate', '100,150', '-channel', 'B', '-gamma', '0.55',
                   '-channel', 'G', '-gamma', '0.7', '+channel', '-gamma', '0.7',
                   rgb, out]

        if self.file_missing(out):
            print(f"Fixing colours")
            subprocess.run(command, cwd=cwd)

        print(f"Done - {out}")

    def parse_arguments(self):
        self.parser = argparse.ArgumentParser(description='Output time of last GOES frame')
        # TODO limit to F, C, M
        self.parser.add_argument('frame', help='Type of frame to fetch: F, C, M')
        self.parser.add_argument('date', nargs=argparse.REMAINDER,
                                  help='Date, in format year day_of_year hour day')

        # + add output filename optional argument
        # + add satellite argument (flag?)
        # ? add 'leave_downloads' argument
        # ? add verbosity flag

        self.parser.parse_args(namespace=self)

        if self.date:
            (self.year, self.doy, self.hour, self.minute) = [int(v) for v in self.date]
            print("Set date from command line arguments")

    def file_missing(self, path):
        return (not os.path.exists(path) and not os.path.isfile(path))

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

        if not os.path.exists(dest) and not os.path.isfile(dest):
            object = self.s3.Object(self.bucket_name, filename).download_file(dest)


if __name__ == '__main__':
    FetchGOES().process()

