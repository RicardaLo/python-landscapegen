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
arcpy.SpatialReference("WGS_1984_UTM_Zone_32N")  # Not tested yet

# NA the polygons without geese on them
inRemapTable = "c:/Users/lada/Desktop/reclass.txt"
# Execute Reclassify
reclsRaster = ReclassByTable(outRaster, inRemapTable,"Polyref","Polyref","AvgNumber","NODATA")
