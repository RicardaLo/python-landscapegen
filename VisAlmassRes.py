# Read ascii of ALMaSS landscape 
# Remap values to goose numbers from sim

# Import system modules
from arcpy import env
import arcpy, traceback, sys, time, gc, os
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
arcpy.env.parallelProcessingFactor = "75%"
# Set local variables
inASCII = "c:/MSV/WorkDirectory/AsciiLandscape.txt"
outRaster = "C:/Users/lada/Desktop/vejlerne"
rasterType = "INTEGER"
try:
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
	# Import the roosts
	# Set the local variables
	in_Table = "c:/Users/lada/Desktop/roosts.txt"
	x_coords = "ALong"
	y_coords = "ALat"
	out_Layer = "roost_layer"
	saved_Layer = "C:/Users/lada/Desktop/roosts.lyr"

	# Make the XY event layer...
	arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer, prj)

	# Print the total rows
	print arcpy.GetCount_management(out_Layer)

	# Save to a layer file
	arcpy.SaveToLayerFile_management(out_Layer, saved_Layer)
except:
	tb = sys.exc_info()[2]
	tbinfo = traceback.format_tb(tb)[0]
	pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     " +        str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
	msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

	arcpy.AddError(msgs)
	arcpy.AddError(pymsg)

	print msgs
	print pymsg

	arcpy.AddMessage(arcpy.GetMessages(1))
	print arcpy.GetMessages(1)
