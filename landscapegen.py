# =======================================================================================================================
# Name: Landscape generator  -  landscapegen
# Purpose: The script convert feature layers to rasters and assemble a surface covering land-use map
# Authors: Flemming Skov & Lars Dalby - September 2015

# IMPORT SYSTEM MODULES
import arcpy, traceback, sys, time, gc, os
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
BaseMap = default
Buildings_c = default
Pylons_c = default
Paths_c = default
Railway_c = default
print " "

#####################################################################################################

try:
# Base map
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
      [219898, 20],[229898, 20],
      [233198, 26], [233298, 26], [233398, 26], [233998, 26], [239998, 26],
      [303211, 40], [303212, 40], [303213, 40], [303214, 40], [603211, 40],
      [603213, 40], [603214, 40], [603311, 40], [603312, 40], [603313, 40], [603314, 40],
      [303111, 50], [303112, 50], [303113, 50], [303114, 50],
      [603111, 50], [603112, 50], [603113, 50], [603114, 50],
      [303311, 60], [303312, 60], [303313, 60], [303314, 60],
      [603911, 95],
      [503911, 69],
      [503913, 69],
      [503914, 69],
      [819898, 90],
      [829898, 80],
      [129898, 121],
      [213998, 2300],
      [999898, 2430]])
    print '... reclassifying BaseMap'
    outReclassify = Reclassify(inRaster, reclassField, remap, "NODATA")
    arcpy.Delete_management(outPath + "BaseMap")
    outReclassify.save(outPath + "BaseMap")

# Pylons 
  if Pylons_c == 1:
    print "Processing pylons ..."
    if arcpy.Exists(outPath + "Pylons"):
      arcpy.Delete_management(outPath + "Pylons")
      print "... deleting existing raster"
    arcpy.Merge_management(['T32_1702ledning_punkt', 'T32_1719ledning_punkt', 'T32_1721ledning_punkt',
    'T32_1756ledning_punkt'], outPath + 'LedningPunkt_merge')
    print '... merging pylon layers'
    eucDistTemp = EucDistance(outPath + "LedningPunkt_merge", "", "1", "")
    print 'calculating euclidian distance'
    rasTemp = Con(eucDistTemp < 1.5, 212, 1)
    rasTemp.save(outPath + "Pylons")

# Buildings
  if Buildings_c == 1:
    print "Processing buildings ..."
    if arcpy.Exists(outPath + "Buildings"):
      print "... deleting existing raster"
      arcpy.Delete_management(outPath + "Buildings")
    print '... merging building layers'
    arcpy.Merge_management(['T32_1702bygning_flate', 'T32_1719bygning_flate', 'T32_1721bygning_flate',
    'T32_1756bygning_flate'], outPath + 'BygningFlate_merge')
    print 'checking geometry'
    arcpy.CheckGeometry_management(outPath + "BygningFlate_merge", outPath + "CG_Result")
    # Table that was produced by Check Geometry tool
    table = outPath + 'CG_Result'
    # Create local variables
    fcs = []
    # Loop through the table and get the list of fcs
    for row in arcpy.da.SearchCursor(table, ("CLASS")):
        # Get the class (feature class) from the cursor
        if not row[0] in fcs:
            fcs.append(row[0])
     
    # Now loop through the fcs list, backup the bad geometries into fc + "_bad_geom"
    # then repair the fc
    print "> Processing {0} feature classes".format(len(fcs))
    for fc in fcs:
        print "Processing " + fc
        lyr = 'temporary_layer'
        if arcpy.Exists(lyr):
            arcpy.Delete_management(lyr)
        
        tv = "cg_table_view"
        if arcpy.Exists(tv):
            arcpy.Delete_management(tv)
    
        arcpy.MakeTableView_management(table, tv, ("\"CLASS\" = '%s'" % fc))
        arcpy.MakeFeatureLayer_management(fc, lyr)
        arcpy.AddJoin_management(lyr, arcpy.Describe(lyr).OIDFieldName, tv, "FEATURE_ID")
        arcpy.CopyFeatures_management(lyr, fc + "_bad_geom")
        arcpy.RemoveJoin_management(lyr, os.path.basename(table))
        arcpy.RepairGeometry_management(lyr)
    print 'converting buildings to raster'
    arcpy.PolygonToRaster_conversion(outPath + "BygningFlate_merge", "OBJTYPE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
    rasIsNull = IsNull(outPath + "tmpRaster")
    rasTemp = Con(rasIsNull == 1, 1, 5)
    rasTemp.save(outPath + "Buildings")
    arcpy.Delete_management(outPath + "tmpRaster")
  
# Paths 
  if Paths_c == 1:
    print "Processing paths  ..."
    if arcpy.Exists(outPath + "Paths"):
      print "... deleting existing raster"
      arcpy.Delete_management(outPath + "Paths")
    print '... merging path layers'
    arcpy.Merge_management(['T32_1702traktorvegsti_linje', 'T32_1719traktorvegsti_linje', 'T32_1721traktorvegsti_linje',
    'T32_1756traktorvegsti_linje'], outPath + 'TraktorvegSti_merge')
    eucDistTemp = EucDistance(outPath + 'TraktorvegSti_merge', "", "1", "")
    rasTemp = Con(eucDistTemp < 1.51, 123, 1)
    rasTemp.save(outPath + "Paths")

# Railway
  if Railway_c == 1:
    print "Processing railway tracks ..."
    if arcpy.Exists(outPath + "Railway"):
      print "... deleting existing raster"
      arcpy.Delete_management(outPath + "Railway")
    print '... merging railway layers'
    arcpy.Merge_management(['T32_1702bane_linje', 'T32_1719bane_linje', 'T32_1721bane_linje',
    'T32_1756bane_linje'], outPath + 'Banelinje_merge')
    eucDistTemp = EucDistance(outPath + 'Banelinje_merge', "", "1", "")
    rasTemp = Con(eucDistTemp < 4.5, 118, 1)
    rasTemp.save(outPath + "Railways")

# Stack
  BaseMap = Raster(outPath + 'BaseMap')
  Buildings = Raster(outPath + 'Buildings')
  Pylons = Raster(outPath + 'Pylons')
  Railways = Raster(outPath + 'Railways')
  Paths = Raster(outPath + 'Paths')

  step1 = Con(Buildings == 1, BaseMap, Buildings)
  step2 = Con(Pylons == 1, step1, Pylons)
  step3 = Con(Paths == 1, step2, Paths)
  step4 = Con(Railways == 1, step3, Railways)

  step4.save(outPath + 'Final')

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