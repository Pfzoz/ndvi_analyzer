import matplotlib.pyplot as plt
import os
import gdal
import rasterio
import numpy as np
from PIL import Image

def normalize(band):
    band_min, band_max = (band.min(), band.max())
    return ((band-band_min)/((band_max-band_min)))

inputPath = "assets/geodata/dump_milho123/input/"
outputPath = "assets/geodata/dump_milho123/output/"

blueName = "T22JCP_20220512T133231_B02_10m.jp2"
greenName = "T22JCP_20220512T133231_B03_10m.jp2"
redName = "T22JCP_20220512T133231_B04_10m.jp2"

## Converts bands from JPEG2000 to GeoTiff

bandList = [band for band in os.listdir(inputPath) if band[-4:] == ".jp2"]
for band in bandList:
    sourceImage = gdal.Open(inputPath+band)
    gdal.Translate(inputPath+band[:-4]+".tif", sourceImage, format="GTiff", outputType=gdal.GDT_Float64)
    raster = rasterio.open(inputPath+band[:-4]+".tif")
    #
    with rasterio.open(inputPath+band[:-4]+"_norm"+".tif", "w+", driver="GTiff", width=raster.width, height=raster.height, count=1, crs=raster.crs, 
    transform=raster.transform, dtype=raster.dtypes[0]) as convertedRaster:
        convertedRaster.write(normalize(raster.read(1)), 1)
        convertedRaster.close()

## Converts into RGB

normalizedBandList = [band for band in os.listdir(inputPath) if band[-9:] == "_norm.tif"]
print(normalizedBandList)
b2 = None
b3 = None
b4 = None

for band in normalizedBandList:
    if "B02" in band:
        b2 = rasterio.open(inputPath+band)
    elif "B03" in band:
        b3 = rasterio.open(inputPath+band)
    elif "B04" in band:
        b4 = rasterio.open(inputPath+band)

with rasterio.open(outputPath+"RGB.tif", "w+", photometric="RGB", driver="GTiff", width=b2.width, height=b2.height, count=3, crs=b2.crs, transform=b2.transform, dtype=b2.dtypes[0]) as rgb:
    rgb.write(b2.read(1), 3)
    rgb.write(b3.read(1), 2)
    rgb.write(b4.read(1), 1)
    rgb.close()

