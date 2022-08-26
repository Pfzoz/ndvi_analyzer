import os
import geopandas
import rasterio as rio
from PIL import Image
import glymur


Image.MAX_IMAGE_PIXELS = 300000000

## Transformando em RGB

# Caminho das imagens: B04 = Red, B03 = Green, B02 = Blue
redPath = "assets/geodata/dump_r2/S2B_MSIL2A_20220815T133149_N0400_R081_T22JCP_20220815T155325.SAFE/GRANULE/L2A_T22JCP_A028421_20220815T133149/IMG_DATA/R10m/T22JCP_20220815T133149_B04_10m.jp2"
greenPath = "assets/geodata/dump_r2/S2B_MSIL2A_20220815T133149_N0400_R081_T22JCP_20220815T155325.SAFE/GRANULE/L2A_T22JCP_A028421_20220815T133149/IMG_DATA/R10m/T22JCP_20220815T133149_B03_10m.jp2"
bluePath = "assets/geodata/dump_r2/S2B_MSIL2A_20220815T133149_N0400_R081_T22JCP_20220815T155325.SAFE/GRANULE/L2A_T22JCP_A028421_20220815T133149/IMG_DATA/R10m/T22JCP_20220815T133149_B02_10m.jp2"

## Pega as bandas

"""
redConv = Image.open(redPath)
redConv.save("red.tiff", "TIFF")
greenConv = Image.open(greenPath)
greenConv.save("green.tiff", "TIFF")
blueConv = Image.open(bluePath)
blueConv.save("blue.tiff", "TIFF")
"""
red = glymur.Jp2k(redPath)
green = glymur.Jp2k(greenPath)
blue = glymur.Jp2k(bluePath)

redD = rio.open(redPath)
greenD = rio.open(greenPath)
blueD = rio.open(bluePath) 

# Cria o arquivo RGB, sendo que driver é o formato, count a quantidade de bandas, crs o sistema de coordenadas referenciadas e transform a afinidade espacial geográfica.
rgb = rio.open("RGB3.tiff", 'w+', photometric="RGB", driver="Gtiff", width=10980, height=10980, count=3, crs=redD.crs, transform=redD.transform, dtype=redD.dtypes[0])
rgb.write(red[:], 1)
rgb.write(green[:], 2)
rgb.write(blue[:], 3)



rgb.close()