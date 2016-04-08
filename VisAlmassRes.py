# Read ascii of ALMaSS landscape 
# Remap values to goose numbers from sim

# Import system modules
from arcpy import env
import arcpy, traceback, sys, time, gc, os
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

# Set local variables
inASCII = "c:/MSV/WorkDirectory/AsciiLandscape.txt"
outRaster = "C:/Users/lada/Desktop/vejlerne"
rasterType = "INTEGER"

# Run ASCIIToRaster
arcpy.ASCIIToRaster_conversion(inASCII, outRaster, rasterType)
# Set spatial reference:
prj = arcpy.SpatialReference("WGS 1984 UTM Zone 32N")
arcpy.DefineProjection_management(outRaster, prj)

# NA the polygons without geese on them
inRemapTable = "c:/Users/lada/Desktop/reclass.txt"
# Execute Reclassify
reclsRaster = ReclassByTable(outRaster, inRemapTable,"Polyref","Polyref","AvgNumber","NODATA")
reclsRaster.save("c:/Users/lada/Desktop/vejlerneGeese")

# ---------------------------------------------------------------- #
# Add the roosts as points on the map:
# Set local variables
out_path = "C:/output"
out_name = "habitatareas.shp"
geometry_type = "POINT"
# template = "study_quads.shp"
has_m = "DISABLED"
has_z = "DISABLED"

# Use Describe to get a SpatialReference object
spatial_reference = arcpy.Describe(outRaster).spatialReference

# Execute CreateFeatureclass
arcpy.CreateFeatureclass_management(out_path, out_name, geometry_type, has_m, has_z, spatial_reference)
