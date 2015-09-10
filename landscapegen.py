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

#CONVERSION  - features to raster layers
BaseMap = 1
Buildings250_c = default
Pylon150_c = default
Paths_c = default
Railway_c = default
print " "

#####################################################################################################

try:
# 1) CONVERSION - from feature layers to raster

  if BaseMap == 1:
    print "Processing BaseMap ..."
    if arcpy.Exists(outPath + "BaseMap"):
      print "... deleting existing raster"
      arcpy.Delete_management(outPath + "BaseMap")

      # Merge the municipalities into a single feature layer
    print '... merging'
    arcpy.Merge_management(['T32_1702ar5_flate', 'T32_1719ar5_flate', 'T32_1721ar5_flate',
    'T32_1756ar5_flate'], outPath + 'AR_merge')
    # Set local variables
    inTable = outPath + "AR_merge"
    fieldName = "COMBI"
    expression = "concat(!ARTYPE!, !ARTRESLAG!, !ARSKOGBON!)"
    codeblock = """def concat(*args):
       # Initialize the return value to an empty string,
       retval = ""
       # For each value passed in...
       for t in args:
         # Convert to a string (this catches any numbers),
         # then remove leading and trailing blanks
         s = str(t).strip()
         # Add the field value to the return value
         if s <> '':
           retval += s
       return int(retval)"""
    # Add field to populate with the concatenated ARTYPE, ARTRESLAG, ARSKOGBON 
    print '... adding field'
    arcpy.AddField_management(inTable, fieldName, "LONG", "", "", 6)
    print '... calculating field'
    arcpy.CalculateField_management(inTable, fieldName, expression, "PYTHON_9.3", codeblock)
    print '... converting features to raster'
    arcpy.PolygonToRaster_conversion(outPath + "AR_merge", "COMBI", outPath + "BaseMap", "CELL_CENTER", "NONE", "1")
    inRaster = outPath + "BaseMap"
    reclassField = "Value"
    remap = RemapValue([[119898, 10],
      [129898, 121],
      [219898, 20],[229898, 20],
      [233198, 26], [233298, 26], [233398, 26],
      [233998, 26], [239998, 26], [303111, 50], [303112, 50], [303113, 50], [303114, 50],
      [303211, 40], [303212, 40], [303213, 40], [303214, 40],
      [603211, 40], [603213, 40], [603214, 40], [603311, 40], [603312, 40], [603313, 40], [603314, 40],
      [603111, 50], [603112, 50], [603113, 50], [603114, 50],
      [303311, 60], [303312, 60], [303313, 60], [303314, 60],
      [603911, 95],
      [503911, 69],
      [503913, 69],
      [503914, 69],
      [819898, 90],
      [829898, 80],
      [213998, 2300],
      [999898, 2430]])
  
# Pylons 
  if Pylon150_c == 1:
    print "Processing pylons ..."
    if arcpy.Exists(outPath + "Pylon150"):
      arcpy.Delete_management(outPath + "Pylon150")
      print "... deleting existing raster"
    arcpy.Merge_management(['T32_1702ledning_punkt', 'T32_1719ledning_punkt', 'T32_1721ledning_punkt',
    'T32_1756ledning_punkt'], outPath + 'LedningPunkt_merge')
    print '... merging'
    eucDistTemp = EucDistance(outPath + "LedningPunkt_merge", "", "1", "")
    print 'calculating euclidian distance'
    rasTemp = Con(eucDistTemp < 1.5, 150, 1)
    rasTemp.save(outPath + "Pylon150")

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
  
# Paths 
  if Paths_c == 1:
    print "Processing paths  ..."
    if arcpy.Exists(outPath + "Paths"):
      arcpy.Delete_management(outPath + "Paths")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("T32_1702traktorvegsti_linje", "", "1", "")
    rasTemp = Con(eucDistTemp < 1.51, 175, 1)
    rasTemp.save(outPath + "Paths")


  endTime = time.strftime('%X %x')
  print ""
  print "Landscape generated: " + endTime

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
# test