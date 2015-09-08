# =======================================================================================================================
# Name: Landscape generator  -  landscapegen
# Purpose: The script convert feature layers to rasters and assemble a surface covering land-use map
# Authors: Flemming Skov & Lars Dalby - September 2015

# IMPORT SYSTEM MODULES
import arcpy, traceback, sys, time, gc
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
nowTime = time.strftime('%X %x')
gc.enable
print "Model landscape generator started: " + nowTime
print "... system modules checked"

# DATA - paths to data, output gdb, scratch folder and model landscape mask
outPath = "c:/Users/lada/Landskabsgenerering/Norge/norway.gdb/"                    # saves maps here
localSettings = "c:/Users/lada/Landskabsgenerering/Norge/project.gdb/NorwayOutlineRaster"   # project folder with mask
gisDB = "c:/Users/lada/Landskabsgenerering/Norge/norwaygis.gdb"                    # input features
scratchDB = "c:/Users/lada/Landskabsgenerering/Norge/scratch"                      # scratch folder for tempfiles
# asciiexp = "c:/Users/lada/Landskabsgenerering/Norge/ASCII_haslev.txt"              # export in ascii (for ALMaSS)
# reclasstable = "c:/Users/lada/Landskabsgenerering/Norge/reclass.txt"               # reclass ascii table

# MODEL SETTINGS
arcpy.env.overwriteOutput = True
arcpy.env.workspace = gisDB
arcpy.env.scratchWorkspace = scratchDB
arcpy.env.extent = localSettings
arcpy.env.mask = localSettings
arcpy.env.cellSize = localSettings
print "... model settings read"

# MODEL EXECUTION - controls which processes are executed

default = 0  # 1 -> run process; 0 -> not run process

#MOSAIC
# vejnet_c = default      #create road theme

#CONVERSION  - features to raster layers
Water_c = default   #land_sea
PublicLanduse100_c = default   #land_sea
Buildings250_c = default
Pylon150_c = 1
Paths_c = 1
print " "

#####################################################################################################

try:

# 1) CONVERSION - from feature layers to raster

# 1 - Water
  if Water_c == 1:
    print "Processing base map (land/sea) ..."
    if arcpy.Exists(outPath + "Water"):
      arcpy.Delete_management(outPath + "Water")
      print "... deleting existing raster"
    arcpy.PolygonToRaster_conversion("T32_1702vann_flate", "OBJTYPE", outPath + "Water", "CELL_CENTER", "NONE", "1")
# Public landuse
  if PublicLanduse100_c == 1:
    print "Processing PublicLanduse ..."
    if arcpy.Exists(outPath + "PublicLanduse"):
      arcpy.Delete_management(outPath + "PublicLanduse")
      print "... deleting existing raster"
    arcpy.PolygonToRaster_conversion("T32_1702arealbruk_flate", "OBJTYPE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
  # Set local variables
  inRaster = outPath + "tmpRaster"
  reclassField = "OBJTYPE"
  remap = RemapValue([["Grustak", 101], ["Tømmervelte", 102],["Steinbrudd", 103],["Anleggsområde", 104],["Gravplass", 105],["Park", 106],
  ["Lekeplass", 107], ["SportIdrettPlass", 108], ["Golfbane", 109], ["IndustriOmråde", 110], ["Fyllplass", 111], ["Fyllplass", 111],
  ["Skytebane", 112], ["Campingplass", 113], ["Rasteplass", 114], ["Steintipp", 115], ["Gruve", 116]])
  # Execute Reclassify
  outReclassify = Reclassify(inRaster, reclassField, remap, "NODATA")
  # Save the output 
  outReclassify.save(outPath + "PublicLanduse")
  arcpy.Delete_management(outPath + "tmpRaster")

# Buildings
  if Buildings250_c == 1:
    print "Processing buildings ..."
    if arcpy.Exists(outPath + "Buildings"):
      arcpy.Delete_management(outPath + "Buildings")
      print "... deleting existing raster"
    arcpy.PolygonToRaster_conversion("T32_1702bygning_flate", "OBJTYPE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
    rasIsNull = IsNull(outPath + "tmpRaster")
    rasTemp = Con(rasIsNull == 1, 1, 250)
    rasTemp.save(outPath + "Buildings")
    arcpy.Delete_management(outPath + "tmpRaster")

# Pylons 
  if Pylon150_c == 1:
    print "Processing pylons ..."
    if arcpy.Exists(outPath + "Pylon150"):
      arcpy.Delete_management(outPath + "Pylon150")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("T32_1702ledning_punkt", "", "1", "")
    rasTemp = Con(eucDistTemp < 1.5, 150, 1)
    rasTemp.save(outPath + "Pylon150")

  endTime = time.strftime('%X %x')
  print ""
  print "Landscape generated: " + endTime

# Paths 
  if Paths_c == 1:
    print "Processing paths  ..."
    if arcpy.Exists(outPath + "Paths"):
      arcpy.Delete_management(outPath + "Paths")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("T32_1702traktorvegsti_linje", "", "1", "")
    rasTemp = Con(eucDistTemp < 1.51, 175, 1)
    rasTemp.save(outPath + "Paths")


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
