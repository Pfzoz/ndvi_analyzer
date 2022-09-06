from genericpath import isdir
import rasterio
from rasterio import mask
import geopandas as gpd
from shapely.geometry import *
import fiona
import os

fiona.drvsupport.supported_drivers['LIBKML'] = 'rw' # Only way for geopandas to read .kml

def remove_third_dimension(geom):
    
    if geom.is_empty:
        return geom

    if isinstance(geom, Polygon):
        exterior = geom.exterior
        new_exterior = remove_third_dimension(exterior)

        interiors = geom.interiors
        new_interiors = []
        for int in interiors:
            new_interiors.append(remove_third_dimension(int))

        return Polygon(new_exterior, new_interiors)

    elif isinstance(geom, LinearRing):
        return LinearRing([xy[0:2] for xy in list(geom.coords)])

    elif isinstance(geom, LineString):
        return LineString([xy[0:2] for xy in list(geom.coords)])

    elif isinstance(geom, Point):
        return Point([xy[0:2] for xy in list(geom.coords)])

    elif isinstance(geom, MultiPoint):
        points = list(geom.geoms)
        new_points = []
        for point in points:
            new_points.append(remove_third_dimension(point))

        return MultiPoint(new_points)

    elif isinstance(geom, MultiLineString):
        lines = list(geom.geoms)
        new_lines = []
        for line in lines:
            new_lines.append(remove_third_dimension(line))

        return MultiLineString(new_lines)

    elif isinstance(geom, MultiPolygon):
        pols = list(geom.geoms)

        new_pols = []
        for pol in pols:
            new_pols.append(remove_third_dimension(pol))

        return MultiPolygon(new_pols)

    elif isinstance(geom, GeometryCollection):
        geoms = list(geom.geoms)

        new_geoms = []
        for geom in geoms:
            new_geoms.append(remove_third_dimension(geom))

        return GeometryCollection(new_geoms)

    else:
        raise RuntimeError("Currently this type of geometry is not supported: {}".format(type(geom)))

def get_all_subdirs(_path : str, include_dir : bool=True):
    returnPaths = []
    if _path[-1] != "/" and _path[-1] != "\\":
        _path = _path + "/"
    for path in os.listdir(_path):
        if os.path.isdir(_path+path):
            if include_dir:
                returnPaths.append(_path+path)
            returnPaths.extend(get_all_subdirs(_path+path, include_dir))
        else:
            returnPaths.append(_path+path)
    return returnPaths

for kmlPath in os.listdir("assets/geodata/imagery"):
    kmlGDF = gpd.read_file("assets/geodata/kml/"+kmlPath.split("/")[-1]+".kml")

    bluePath, greenPath, redPath = (None, None, None)

    for path in get_all_subdirs("assets/geodata/imagery/"+kmlPath):
        if "B02" in path:
            bluePath = path
        elif "B03" in path:
            greenPath = path
        elif "B04" in path:
            redPath = path
    
    print("-->Processing "+kmlPath+" rasters.")

    for i, shape in enumerate(kmlGDF["geometry"]):
        kmlGDF.at[i, "geometry"] = remove_third_dimension(kmlGDF.at[i, "geometry"])
        

    footprint = kmlGDF.at[i, "geometry"]

    b2 = rasterio.open(bluePath)
    b3 = rasterio.open(greenPath)
    b4 = rasterio.open(redPath)

    print("-->Creating RGB raster ("+kmlPath+")")

    if not os.path.exists("assets/geodata/imagery/"+kmlPath+"/output"):
        os.mkdir("assets/geodata/imagery/"+kmlPath+"/output")

    with rasterio.open("assets/geodata/imagery/"+kmlPath+"/output/RGB.tif"
        , 'w', driver="GTiff", width=b4.width, height=b4.height, count=3, 
        crs=b4.crs, transform=b4.transform, dtype=b4.dtypes[0], photometric="RGB") as rgb:
        rgb.write(b2.read(1), 1)
        rgb.write(b3.read(1), 2)
        rgb.write(b4.read(1), 3)
        rgb.close()
    
    print("-->"+kmlPath+" CRS = epsg:"+str(b4.crs).split(":")[-1])

    kmlProjection = kmlGDF.to_crs({"init": "epsg:"+str(b4.crs).split(":")[-1]})

    with rasterio.open("assets/geodata/imagery/"+kmlPath+"/output/RGB.tif") as src:
        outImage, outTransform = mask.mask(src, kmlProjection.geometry, crop=True)
        outMeta = src.meta.copy()
        outMeta.update(
            {
                "driver": "GTiff",
                "height": outImage.shape[1],
                "width": outImage.shape[2],
                "transform": outTransform
            }
        )

    print("-->Creating mask ("+kmlPath+")")

    with rasterio.open("assets/geodata/imagery/"+kmlPath+"/output/RGB_masked.tif", 'w',
        **outMeta, photometric="RGB") as dest:
        dest.write(outImage)
    
    dest.close()
    src.close()


exit(0)
    

kmlGDF = gpd.read_file("assets/geodata/region2_kml/milho123.kml") # polygon-containing kml file.

bluePath = "assets/geodata/dump_milho123/input/T22JCP_20220512T133231_B02_10m.jp2"
greenPath = "assets/geodata/dump_milho123/input/T22JCP_20220512T133231_B03_10m.jp2"
redPath = "assets/geodata/dump_milho123/input/T22JCP_20220512T133231_B04_10m.jp2"

print(kmlGDF) # The CRS of this geometry is 4326

## The polygon in the kml file is a 3D shape, here there is a function created by Rauni: https://gis.stackexchange.com/users/14466/rauni to reshape it.



for i, shape in enumerate(kmlGDF["geometry"]):
    print("\n--> 3D Polygon\n", kmlGDF.at[i, "geometry"])
    kmlGDF.at[i, "geometry"] = remove_third_dimension(kmlGDF.at[i, "geometry"])
    print("\n--> Reshaped 2D Polygon\n", kmlGDF.at[i, "geometry"])

## Reading of bands

footprint = kmlGDF.at[0, "geometry"] # Polygon object itself

b2 = rasterio.open(bluePath)
b3 = rasterio.open(greenPath)
b4 = rasterio.open(redPath)
print(b4.crs)

## Creationg of RGB image

with rasterio.open("RGB.tif", 'w', driver="GTiff", width=b4.width, height=b4.height, count=3, crs=b4.crs, transform=b4.transform, 
    dtype=b4.dtypes[0], photometric="RGB") as rgb:
    rgb.write(b2.read(1), 1)
    rgb.write(b3.read(1), 2)
    rgb.write(b4.read(1), 3)
    print(rgb.crs)
    rgb.close()

print("epsg:"+str(b4.crs).split(":")[-1])

## Changes the coordinate system (crs) of the polygon to the same of the satellite image

kmlProjection = kmlGDF.to_crs({"init": "epsg:"+str(b4.crs).split(":")[-1]})

## Here we mask the image with the projected boundary


with rasterio.open("RGB.tif") as src:
    print(src.photometric)
    print(src.read(1) == b2.read(1))
    outImage, outTransform = mask.mask(src, kmlProjection.geometry, crop=True)
    outMeta = src.meta.copy()
    outMeta.update(
        {
            "driver": "GTiff",
            "height": outImage.shape[1],
            "width": outImage.shape[2],
            "transform": outTransform
        }
    )

with rasterio.open("RGB_Masked.tif", 'w', **outMeta, photometric="RGB") as dest:
    dest.write(outImage)

dest.close()
src.close()