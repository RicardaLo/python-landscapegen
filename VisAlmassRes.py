# Read ascii of ALMaSS landscape 
# Remap values to goose numbers from sim

# Import system modules
import arcpy
arcpy.CheckOutExtension("Spatial")

# Set local variables
inASCII = "c:/MSV/WorkDirectory/AsciiLandscape.txt"
outRaster = "C:/Users/lada/Desktop/vejlerne"
rasterType = "INTEGER"

# Execute ASCIIToRaster
arcpy.ASCIIToRaster_conversion(inASCII, outRaster, rasterType)

# NA the polygons without geese on them
inRaster = outRaster
inRemapTable = #  Insert fieldforage file which have been subset down to only goose filds and have a column with
# Polyref and Avg number
# Execute Reclassify
outRaster = ReclassByTable(inRaster, inRemapTable,"Polyref","Polyref","AvgNumber","NODATA")
