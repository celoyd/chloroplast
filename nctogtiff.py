# python nctogtiff.py in.nc out.tif
# Convert a GOES-16 netCDF's Rad (radiance) field to a geotiff.

# This is a fairly weird/opinionated script. Big gotchas:
#
# 1. We use both the netCDF library and rasterio, even through
#    we could make do with either one alone. netCDF reads out
#    the data much faster (bypassing GDAL’s driver, which is
#    very slow on GOES-16 netCDF files, I *think* because of
#    an interaction between how it's compressed and the fact
#    that it's south-up). Rasterio, on the other hand, is useful
#    because it reads the georeferencing tags in a convenient
#    form, letting us skip an explicit conversion from the way
#    the netCDF stores it (which I would not trust myself to
#    implement robustly anyway).
#
# 2. The scaleup_factor is just an arbitrary number that seems
#    to scale real-world radiance values well into the uint16
#    valid data range. It might lead to quantization for a
#    file with very small values, or overflow for one with very
#    large values. So watch out, especially outside the visible.
#
# 3. We do a little dance to read the data out upside-down.
#    Output is south-up (but correctly georeferenced, so it
#    easily reprojects to north-up). Ideally (TODO), we would
#    write a north-up TIFF with a flipped transform.

import rasterio as rio
from rasterio.windows import Window
from sys import argv
import numpy as np
from netCDF4 import Dataset
from affine import Affine


# Arbitrary scaling factor to store smallish values in a
# uint16 packages without excessive quantization:
scaleup_factor = 64

srcf, dstf = argv[1:]

# Use rasterio to get the georeferencing:
with rio.open(f'NETCDF:"{srcf}":Rad') as rio_src:
    meta = rio_src.profile

nc = Dataset(srcf, fill_value=False)
# Use netCDF to get the data scaled to PN:
src = nc.variables["Rad"]
nodata = src._FillValue

height, width = src.shape[:2]

# The raw files have odd shapes, so we set some odd block
# sizes. TODO: test different block sizes and clean this up.
bs = 500 * 2
if width % bs != 0:
    bs = 904
if width in (10848, 21696):
    bs = 678 * 2

assert width % bs == 0
assert height % bs == 0

width_block_count = int(width / bs)
height_block_count = int(height / bs)


meta.update(
    {
        "driver": "GTiff",
        "width": width,
        "height": height,
        "count": 1,
        "dtype": np.uint16,
        "compression": "deflate",
        # "transform": newaff
    }
)


def scale(n):
    # We reserve 0 for nodata, slightly fudging truly 0 pixels,
    # but this appears to be under the noise floor anyway.
    # (TODO: check that "appears" on a wide range of data.)
    sn = np.clip((n * scaleup_factor), 1, 65535).astype(np.uint16)
    sn[n == nodata] = 0
    return sn


def flip_window(w):
    # Turn a slice into a window, and also reflect it vertically
    # in the list of rows of windows (e.g., the top left slice becomes
    # the bottom left window):
    m = Window.from_slices((height - w[0][1], height - w[0][0]), (w[1][0], w[1][1]))
    return m


with rio.open(dstf, "w", **meta) as dst:

    slices = (
        ((v * bs, (v + 1) * bs), (h * bs, (h + 1) * bs))
        # This order is important for speed:
        for v in range(height_block_count)
        for h in range(width_block_count)
    )

    for sl in slices:
        rad = src[sl[0][0] : (sl[0][1]), sl[1][0] : (sl[1][1])]
        rad = scale(np.array(rad))
        rad = np.flipud(rad)
        w = flip_window(sl)
        dst.write(rad, 1, window=w)
