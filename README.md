# chloroplast

Tools for working with data from the ABI sensor on GOES-R satellites in Python and shell.

This is late alpha to early beta quality. Many, many things about it will change. Documentation may be missing or wrong. Installation and dependencies, in particular, are under-documented.

Dependencies include but are not necessarily limited to:

- `awscli` (and its CLI: `aws` should work in your terminal)
- `rasterio` and `rio-mucho` (ditto `rio` ditto)
- `netCDF4`
- `ImageMagick` as a system utility (soon to be replacaed by `rio-color`)
- `jq` as a system utility.
- GNU `parallel` (_not_ the one in `moreutils`) as a system utility
- `gdal` (package may be called `gdal-bin`) as a system utility

After installing, here’s the easiest way to see something pretty:

1. Find your Julian day (day of year, or DOY) in the UTC time zone. I do this with an alias called `doyu` that calls postgres, because postgres’s time tools are good: `psql -At -d postgres -c "select extract(doy from now() at time zone 'UTC')`.

2. Find your year, hour, and minute at UTC. I have an alias called `dhmu` (day, hour, minute UTC): ```echo `date -u "+%Y"` `doyu` `date -u "+%H %M"` ```. Say this is `2018 256 17 38`.

3. Round down to the nearest minute ending in 7 or 2, so `2018 256 17 37`. If that’s less than about 5 minutes ago, go back to the previous one. That’s `2018 256 17 32`. 

4. Run `./rgb_frame.sh C 2018 256 17 32 test.tif` . `C` means the contiguous UC frame, and `test.tif` is your target file. You should see a lot of output as it starts downloading and working.

If everything worked, you will now have a reasonable RGB image in `test.tif`, plus an intermediate file called `20182561732.rgb.tif`, which has no color formula applied.

Both TIFFs are properly georeferenced; you can do, for example, `gdalwarp -t_srs EPSG:3857 test.tif test-webmerc.tif` and it should just work.

You can also crop out an area of interest; `alberta.sh` is an example that cuts out the West Coast and puts it in an appropriate projection. (It’s called that because the way the cutlines work, it has roughly the outline of Alberta. Sorry.)

The available frames types are: `F` for full disk (every quarter of the hour, on the quarter), `C` for the contiguous US (every five minutes, on the 2s and 7s), and `M` for the mesoscale floating window, up to every 30 seconds. (I think there might be two windows? I haven’t worked much with them.)

Look in the code to see how things are split up. For example, if you just want to pull one band, you can use `list-prefix.sh` and `get.sh`.


## To do

- Installation instructions
- Generally cleaner code (less bash)
- Be nicer to the filesystem: use temp files properly, etc.
- Support the every-30-second M window (i.e., fix the assumption that there will be only 0 or 1 images available for any given minute)
- An optimization pass, especially to avoid touching the disk so much
- Replace `convert` with parallelized `rio color`
- Parameterize everything better: color formulas, prepare for GOES-17, etc.
- Options to mask missing pixels
- Tutorial on using `parallel`
- Tutorial on animation
- Better tools for handling time: pythonize `dhmu`; write a tool for “get me the first available X frame before hh:mm”, etc.
