#!/usr/bin/env python

# weight.py input1.tif w1:w2 input2.tif output.tif
# Make a weighted average of input{1,2}.tif (both single-band)
# with weight per the w1:w2 ratio. Example:
# weight.py green.tif 7:1 nir.tif synthesized-green.tif

import rasterio as rio
from sys import argv
import numpy as np
import riomucho


def weight(ab, window, ij, g):
    ab = np.array(ab).astype(np.float32)
    weighted = (ab[0] * g["weights"][0] + ab[1] * g["weights"][1]) / (
        g["weights"][0] + g["weights"][1]
    )
    return weighted.astype(g["dtype"])


def preprocess(file1, file2, output, ratio):
    processes = 4

    g = {"dtype": np.uint16, "weights": list(map(float, ratio.split(":")))}

    with rio.open(file1) as src:
        windows = [[window, ij] for ij, window in src.block_windows()]
        options = src.profile
        options.update({"count": 1, "compress": "lzw"})

    with riomucho.RioMucho(
        [file1, file2], output, weight, windows=windows, global_args=g, options=options
    ) as mucho:
        mucho.run(processes)

if __name__ == '__main__':
    file1, ratio, file2, output = argv[1:]
    preprocess(file1, file2, output, ratio)
