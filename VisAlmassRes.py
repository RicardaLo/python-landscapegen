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

# Execute ASCIIToRaster
arcpy.ASCIIToRaster_conversion(inASCII, outRaster, rasterType)

# NA the polygons without geese on them
inRemapTable = "c:/Users/lada/Desktop/reclass.txt"
# Execute Reclassify
reclsRaster = ReclassByTable(outRaster, inRemapTable,"Polyref","Polyref","AvgNumber","NODATA")
