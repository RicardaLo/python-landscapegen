# =======================================================================================================================
# Name: Landscape generator  -  landscapegen
# Purpose: Convert feature layers to rasters and assemble a surface covering land-use map
# Author: Lars Dalby - September 2015
# The script is a modified version of the original landscape generator script
# developed by Skov & Dalby. See http://www.biorxiv.org/content/early/2015/08/31/025833 or
# http://www.sciencedirect.com/science/article/pii/S0048969715308597
# doi:10.1016/j.scitotenv.2015.10.042

# Import system modules
from arcpy import env
import arcpy, traceback, sys, time, gc, os, csv
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
nowTime = time.strftime('%X %x')
arcpy.env.parallelProcessingFactor = "75%"
print "Model landscape generator started: " + nowTime
print "... system modules checked"

# Data - paths to data, output gdb, scratch folder and model landscape mask
# All data have prior to running the script been imported into a file geodatabase
# with the desired resolution.
staticpath = "o:/ST_LandskabsGenerering/Norway/NTrondelag/"
outPath = os.path.join(staticpath, "Landscape", "NTrondelag.gdb/")                  # Maps are stored here
localSettings = os.path.join(staticpath, "Landscape", "project.gdb/NTrondelagOutlineRaster")  # project folder with mask
gisDB = os.path.join(staticpath, "RawData","NTrondelaggis.gdb")                      # input features
scratchDB = os.path.join(staticpath,"scratch")                        # scratch folder for tempfiles
asciiexp = os.path.join(staticpath, "Landscape","outputs", "ASCII_NTrondelag.txt") # export in ascii (for ALMaSS)
attrexp =  os.path.join(staticpath, "Landscape","outputs", "Attr_NTrondelag.csv")      # export attribute table (for ALMaSS)

# Model settings
arcpy.env.overwriteOutput = True
arcpy.env.workspace = gisDB
arcpy.env.scratchWorkspace = scratchDB
arcpy.env.extent = localSettings
arcpy.env.mask = localSettings
arcpy.env.cellSize = localSettings
print "... model settings read"

# Model execution - controls which processes are executed

default = 0  # 1 -> run process; 0 -> not run process

# Conversion  - features to raster layers
Preparation = 1
BaseMap = default
Buildings_c = default
Pylons_c = default
Paths_c = default
Railway_c = default
CompleteMap_c = default  # Requires all the above layers
Regionalize_c = default  # Requires the CompleteMap
ConvertAscii_c = default  # Requires the RegionalizedMap
print " "

#####################################################################################################

try:
# Basic preparation of maps and data
  if Preparation == 1:
    print "Preparing and cleaning data  ..."
    print('... deleting existing data')
    if arcpy.Exists(outPath + "MAT_merge"):
      arcpy.Delete_management(outPath + "MAT_merge")
    if arcpy.Exists(outPath + "AR_merge"):
      arcpy.Delete_management(outPath + "AR_merge")      
    if arcpy.Exists(outPath + "combi_identify"):
      arcpy.Delete_management(outPath + "combi_identify")
    if arcpy.Exists(outPath + "combi_single"):
      arcpy.Delete_management(outPath + "combi_single")
    if arcpy.Exists(outPath + "combi_final"):
      arcpy.Delete_management(outPath + "combi_final")

    print('... merging flate maps')
    arcpy.Merge_management(['T32_1702ar5_flate', 'T32_1719ar5_flate', 'T32_1721ar5_flate',
    'T32_1756ar5_flate', 'T32_1724ar5_flate', 'T32_1725ar5_flate'], outPath + 'AR_merge')
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
    print '..... adding field'
    arcpy.AddField_management(inTable, fieldName, "LONG", "", "", 6)
    print '..... calculating field'
    arcpy.CalculateField_management(inTable, fieldName, expression, "PYTHON_9.3", codeblock)

    # Merge the 'matrikkel'maps into a single feature layer
    print '... merging matrikkel maps'
    matpath = "O:/ST_LandskabsGenerering/Norway/NTrondelag/RawData/Matrikkeldata/MatrikkelEdited.gdb/"
    arcpy.Merge_management([matpath + 'mat32_1702', matpath + 'mat32_1719', matpath + 'mat32_1721',
    matpath + 'mat32_1724', matpath + 'mat32_1725', matpath + 'mat32_1756'], outPath + 'MAT_merge')
    # Set local variables
    inTable = outPath + "MAT_merge"
    fieldName = "FARMID"
    expression = "concat(!MATRIKKELK!, !GNR!, !BNR!)"
    codeblock = """def concat(*args):
       # Initialize the return value to an empty string,
       retval = ""
       # For each value passed in...
       for t in args:
         # Convert to a string (this catches any numbers), then remove leading and trailing blanks
         s = str(t).strip()
         # Add the field value to the return value and a '-' (removes the final '-' before return)
         if s <> '':
           retval += s
           retval += '-'
       retval = retval[:-1]
       return (retval)""" 
    # Add field to populate with the concatenated MATRIKKELK, GNR, BNR 
    print '..... adding field'
    arcpy.AddField_management(inTable, fieldName, "TEXT", "", "", 20 )
    print '..... calculating field'
    arcpy.CalculateField_management(inTable, fieldName, expression, "PYTHON_9.3", codeblock)

    # combining matrikkel and flate maps using identify commando
    print('... combining matrikkel and flate maps')
    arcpy.Identity_analysis (outPath + 'AR_merge', outPath + 'MAT_merge', outPath + 'combi_identify')
    
    # repair command - just in case
    print('... repairing geometry')
    arcpy.RepairGeometry_management (outPath + 'combi_identify')

    # multi- to singlepart command
    print('... running multi- to singlepart command')
    arcpy.MultipartToSinglepart_management(outPath + 'combi_identify', outPath + 'combi_single')

    # calculate area for each individual polygon in square meters
    print('... calculating area for each polygon')
    arcpy.AddGeometryAttributes_management(outPath + 'combi_single', 'AREA', 'METERS', 'SQUARE_METERS' )

    # eliminate sliver polygons
    print('... remove sliver polygons')
    # Execute MakeFeatureLayer
    arcpy.MakeFeatureLayer_management(outPath + 'combi_single', "blocklayer") 
    # Execute SelectLayerByAttribute to define features to be eliminated - POLY_AREA in sq.meters
    arcpy.SelectLayerByAttribute_management("blocklayer", "NEW_SELECTION", '"POLY_AREA" < 150')
    # Execute Eliminate for all polygons exept the road polygons (ARTTYPE = 12)
    arcpy.Eliminate_management("blocklayer", outPath + "combi_final", "LENGTH", '"ARTYPE" = 12')
    # Recalculate the area
    # Remove fields that are not needed (incl the POLY_AREA that needs recalculation)
    dropFields = ["FID_AR_merge", "POLY_", "POLY_ID", "KOORDH", "OBJTYPE", "ARKARTSTD", 
                  "DATFGSTDAT", "VERIFDATO", "MALEMETODE", "NOYAKTIGHE", "SYNBARHET", "PRODUKT", 
                  "VERSJON", "OMRADEID", "ORGDATVERT", "KOPIDATO", "OPPHAV", "FID_MAT_merge", "POLY1", 
                  "POLY_ID_1", "KOORDH_1", "OBJTYPE_1", "HOVEDTEIG", "PUNKTFESTE", "TVIST", 
                  "UREGJORDSA", "AVKLARTEIE", "TEIGMEDFLE", "TEIGFLEREM", "AREAL", "AREALMERKN", 
                  "KOBLING_ID", "OMRADEID_1", "ORGDATVERT_1", "KOPIDATO_1", "OBJECTID_1", 
                  "Shape_Leng", "ORIG_FID", "POLY_AREA"]
    # Execute DeleteField
    arcpy.DeleteField_management(outPath + "combi_final", dropFields)
    # Recalculate area for each individual polygon in square meters
    print('... recalculating area for each polygon')
    arcpy.AddGeometryAttributes_management(outPath + 'combi_final', 'AREA', 'METERS', 'SQUARE_METERS' )
    # Make unique field ID's
    print '..... adding field'
    arcpy.AddField_management(outPath + 'combi_final', 'CODE', "LONG", "", "", 12)
    print '..... calculating field'

    fc = outPath + 'combi_final'
    fields = ['ARTYPE', 'CODE']

    num21 = 2100000
    num22 = 2200000
    num23 = 2300000

    # Create update cursor for feature class 
    # For each row, evaluate the ARTYPE value (index position of 0), and update field CODE (index position of 1)

    with arcpy.da.UpdateCursor(fc, fields) as cursor: 
      for row in cursor:
        if (row[0] == 21):
            row[1] = num21
            num21 = num21 + 1
        elif (row[0] == 22):
            row[1] = num22
            num22 = num22 + 1
        elif (row[0] == 23):
            row[1] = num23
            num23 = num23 + 1
        else:
            row[1] = row[0]

        # Update the cursor with the updated list
        cursor.updateRow(row)


# Base map
  if BaseMap == 1:
    print "Processing BaseMap ..."
    if arcpy.Exists(outPath + "BaseMap"):
      print "... deleting existing raster"
      arcpy.Delete_management(outPath + "BaseMap")

    print '... converting features to raster' 
    #NB NB  not preliminary layer 'combi_final_fields' is not calculated automatically
    
    arcpy.PolygonToRaster_conversion(outPath + "combi_final", "CODE", outPath + "BaseMap", "CELL_CENTER", "NONE", "1")
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
      [503911, 69],
      [503913, 69],
      [503914, 69],
      [829898, 80],
      [819898, 90],
      [603911, 95],
      [129898, 121],
      [213998, 69],
      [999898, 69]])

    # Missing data currently mapped to bare rock as it is outside the area of interest for the goose modelling.
    print '... reclassifying BaseMap'

    outReclassify = Reclassify(inRaster, reclassField, remap, "DATA")
    arcpy.Delete_management(outPath + "BaseMap")
    outReclassify.save(outPath + "BaseMap")

# Pylons 
  if Pylons_c == 1:
    print "Processing pylons ..."
    if arcpy.Exists(outPath + "Pylons"):
      arcpy.Delete_management(outPath + "Pylons")
      print "... deleting existing raster"
    arcpy.Merge_management(['T32_1702ledning_punkt', 'T32_1719ledning_punkt', 'T32_1721ledning_punkt',
    'T32_1756ledning_punkt', 'T32_1724ledning_punkt','T32_1725ledning_punkt'], outPath + 'LedningPunkt_merge')
    print '... merging pylon layers'
    eucDistTemp = EucDistance(outPath + "LedningPunkt_merge", "", "1", "")
    print '... calculating euclidian distance'
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
    'T32_1756bygning_flate', 'T32_1724bygning_flate', 'T32_1725bygning_flate'], outPath + 'BygningFlate_merge')
    print '... checking geometry'
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
    print "..... processing {0} feature classes".format(len(fcs))
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
    print '... converting buildings to raster'
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
    'T32_1756traktorvegsti_linje', 'T32_1724traktorvegsti_linje', 'T32_1725traktorvegsti_linje'], outPath + 'TraktorvegSti_merge')
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
    'T32_1756bane_linje', 'T32_1724bane_linje', 'T32_1725bane_linje'], outPath + 'Banelinje_merge')
    eucDistTemp = EucDistance(outPath + 'Banelinje_merge', "", "1", "")
    rasTemp = Con(eucDistTemp < 4.5, 118, 1)
    rasTemp.save(outPath + "Railways")

# Stack
  if CompleteMap_c == 1:
    print '... loading individual rasters'
    BaseMap = Raster(outPath + 'BaseMap')
    Buildings = Raster(outPath + 'Buildings')
    Pylons = Raster(outPath + 'Pylons')
    Railways = Raster(outPath + 'Railways')
    Paths = Raster(outPath + 'Paths')
    print '... stacking'
    step1 = Con(Buildings == 1, BaseMap, Buildings)
    print 'Buildings added to BaseMap'
    step2 = Con(Pylons == 1, step1, Pylons)
    print 'Pylons added to BaseMap'
    step3 = Con(Paths == 1, step2, Paths)
    print 'Pylons added to BaseMap'
    step4 = Con(Railways == 1, step3, Railways)
    print 'stacking done - saving map'
    step4.save(outPath + 'CompleteMap')

# Regionalise map
  if Regionalize_c == 1:
    print 'Regionalizing...'
    RegionalizedMap = RegionGroup(outPath + 'CompleteMap',"EIGHT","WITHIN","ADD_LINK","")
    RegionalizedMap.save(outPath + "FinalMap")
    nowTime = time.strftime('%X %x')
    print "Regionalization done... " + nowTime

 # Export attribute table 
    table = outPath + "FinalMap"
    # Write an attribute tabel - based on this answer:
    # https://geonet.esri.com/thread/83294
    # List the fields
    fields = arcpy.ListFields(table)  
    field_names = [field.name for field in fields]  
    
    with open(attrexp,'wb') as f:  
      w = csv.writer(f)  
      # Write the headers
      w.writerow(field_names)  
      # The search cursor iterates through the 
      for row in arcpy.SearchCursor(table):  
        field_vals = [row.getValue(field.name) for field in fields]  
        w.writerow(field_vals)  
        del row
    print "Attribute table exported..." + nowTime 

# convert regionalised map to ascii
  if ConvertAscii_c == 1:
    print 'Converting to ASCII...'
    arcpy.RasterToASCII_conversion(outPath + "FinalMap", asciiexp)
    nowTime = time.strftime('%X %x')
    print "Conversion to ASCII done... " + nowTime

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
