# =======================================================================================================================
# Name: Landscape generator  -  landscapegen
# Purpose: The script convert feature layers to rasters and assemble a surface covering land-use map
# Authors: Flemming Skov & Lars Dalby - Oct-Dec 2014
# Last large update: October 19, 2014
# Note:  This version uses the new field polygon theme that covers all of Denmark

#===== Chunk: Setup =====#
# Import system modules
import arcpy, traceback, sys, time, shutil, os
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
nowTime = time.strftime('%X %x')
print "Model landscape generator started: " + nowTime
print "... system modules checked"

# Names of the new landscapes
NJ = ['NJ1', 'NJ2', 'NJ3', 'NJ4', 'NJ5', 'NJ6']
VJ = ['VJ1', 'VJ2', 'VJ3', 'VJ4', 'VJ5']
OJ = ['OJ1', 'OJ2', 'OJ3', 'OJ4']
FU = ['FU1', 'FU2', 'FU3', 'FU4']
NS = ['NS1', 'NS2', 'NS3', 'NS4']
SS = ['SS1', 'SS2', 'SS3', 'SS4', 'SS5', 'SS6']

landscapes = NJ + VJ + OJ + FU + NS + SS
landscapes.append("BO1")  # Different approach is need to apapend only 1 string

# Temporary test with Ostjylland:
landscapes = OJ[0:2]

# Path to the template directory:
template = "o:/ST_LandskabsGenerering/gis/skabelon/" 

# Path to the destination
dst = "c:/Users/lada/Desktop/NewSet/"

# Copy the template directory
for index in range(len(landscapes)):
  dstpath = os.path.join(dst, landscapes[index])
  shutil.copytree(template, dstpath)
  gdbpath = os.path.join(dstpath, "KvadratX.gdb")
  newgdbpath = os.path.join(dstpath, landscapes[index])
  os.rename(gdbpath, newgdbpath + ".gdb")                    

  # Data - paths to data, output gdb, scratch folder and simulation landscape mask
  outPath = os.path.join(dst, landscapes[index], landscapes[index] + ".gdb/")
  gisDB = "c:/Users/lada/Desktop/dkgis.gdb"                               # input features
  scratchDB = os.path.join(dst, landscapes[index], "scratch")             # scratch folder for tempfiles
  asciifile = "ASCII_" + landscapes[index] + ".txt"
  asciiexp = os.path.join(dst, landscapes[index], asciifile)              # export in ascii (for ALMaSS)
  reclasstable = os.path.join(dst, landscapes[index], "reclass.txt")      # reclassification for almass
  # Select the landscape and convert to raster
  # Set local variables
  in_features = "o:/ST_LandskabsGenerering/harelav/gis/harelav.gdb/kvadrater"
  out_feature = os.path.join(dst, landscapes[index] + "/project.gdb/polymask") 
  # Define function to construct WHERE clause:
  def buildWhereClause(table, field, value):
    """Constructs a SQL WHERE clause to select rows having the specified value
    within a given field and table."""

    # Add DBMS-specific field delimiters
    fieldDelimited = arcpy.AddFieldDelimiters(table, field)

    # Determine field type
    fieldType = arcpy.ListFields(table, field)[0].type

    # Add single-quotes for string field values
    if str(fieldType) == 'String':
        value = "'%s'" % value

    # Format WHERE clause
    whereClause = "%s = %s" % (fieldDelimited, value)
    return whereClause
  
  fieldname = "NAME"
  fieldvalue = landscapes[index]
  where_clause = buildWhereClause(in_features, fieldname, fieldvalue)
  
  # Execute Select
  arcpy.Select_analysis(in_features, out_feature, where_clause)
  
  mask = os.path.join(dst, landscapes[index] + "/project.gdb/mask")
  arcpy.PolygonToRaster_conversion(out_feature, "OBJECTID", mask, "CELL_CENTER", "NONE", "1")
  localSettings = mask   # project folder with mask

  # Model settings
  arcpy.env.overwriteOutput = True
  arcpy.env.workspace = gisDB
  arcpy.env.scratchWorkspace = scratchDB
  arcpy.env.extent = localSettings
  arcpy.env.mask = localSettings
  arcpy.env.cellSize = localSettings
  print "... model settings read"
  
  # Model execution - controls which processes to run:
  default = 0  # 1 -> run process; 0 -> do not run process
  
  # Mosaic
  road = default      #create road theme
  builtup = default #create built up theme
  nature = default       #create nature theme
  wetnature = default   #create wet nature theme
  freshwater = default   #create fresh water theme
  cultural = default      #create cultural feature theme
  finalmap = default      #assemble final map
  
  # Conversion  - features to raster layers
  landsea = 1   #land_sea
  slopes_105 = default   #slopes along roads
  roadsideverge_110 = default   #road verges
  paths_112 = default   #paths
  parks_114 = default   #parking areas
  dirtroads_115 = default   #unpaved roads and tracks
  railways_120 = default   #railways
  smallroads_122 = default   #small roads (< 3 meter)
  mediumroads_125 = default   #medium sized roads (3-6 meter)
  largeroads_130 = default   #large roads (> 6 meter)
  pylons_150 = default   #pylons
  windturbines_155 = default   #wind turbines
  builtuplow_205 = default   #built up areas low
  builtuphigh_210 = default   #built up areas high
  citycenter_215 = default   #city center
  industry_220 = default   #industrial areas
  churchyard_225 = default   #Churchyards
  sportsfields_230 = default   #sports areas
  buildings_250 = default   #buildings
  forests_310 = default   #top10dk forest
  shrubs_315 = default   #top10dk shrub
  sand_320 = default   #top10dk sand flats
  heathland_325 = default   #top10dk heath land
  wetland_330 = default   #top10dk wetland
  meadowprotected_355 = default   #protected meadows
  heathlandprotected_360 = default   #protected heath land
  bog_365 = default   #protected bog
  drygrassland_370 = default   #protected dry grassland
  marshprotected_375 = default   #protected salt marshes
  lakesprotected_380 = default   #protected lakes
  lakes_440 = default   #lakes
  smallstreams_435 = default   #small streams (< 2.5 meter)
  mediumstreams_436 = default   #medium streams (2.5 - 12 meter)
  largestreams_437 = default   #large streams (> 12 meter)
  lakebuffer_420 = default   #lake buffer
  fields_1000 = default  #fields
  dikes_620 = default   #dikes
  archeological_625 = default   #archeological sites
  recreational_630 = default   #recreational areas
  hedgerows_635 = default   #hedgerows
  coppice_640 = default   #tree groups
  individualtrees_641 = default   #individual trees
  gravelpits_650 = default   #gravel pits
  ais_1100 = default   #ais landcover map
  
  #NB: these buffers are calculated automatically - mentioned here to keep track on codes
  #aarn425    #buffers small streams
  #aarn426    #buffers medium streams
  #aarn427    #buffers large streams
  
  print " "
  #===== End chunk: setup =====#
  
  #####################################################################################################
  
  try:
  
  #===== Chunk: Conversion =====#
  # from feature layers to raster
  
  # 1 - land and sea (land_hav)
    if landsea == 1:
      print "Processing base map (land/sea) ..."
      if arcpy.Exists(outPath + "landhav"):
        arcpy.Delete_management(outPath + "landhav")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("land_hav", "Land", outPath + "landhav", "CELL_CENTER", "NONE", "1")
  
  # 105 - slopes along larger roads (skrt105)
    if slopes_105 == 1:
      print "Processing artificial slopes along larger roads ..."
      if arcpy.Exists(outPath + "skrt105"):
        arcpy.Delete_management(outPath + "skrt105")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("skraent","","1","")
      rasTemp = Con(eucDistTemp < 2.5, 105, 1)
      rasTemp.save(outPath + "skrt105")
  
  # 110 - road verges (vejk110)
    if roadsideverge_110 == 1:
      print "Processing road verges ..."
      if arcpy.Exists(outPath + "vejk110"):
        arcpy.Delete_management(outPath + "vejk110")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("vejkant","","1","")
      rasTemp = Con(eucDistTemp < 1.75, 110, 1)
      rasTemp.save(outPath + "vejk110")
  
  # 112 - paths (stie112)
    if paths_112 == 1:
      print "Processing paths  ..."
      if arcpy.Exists(outPath + "stie112"):
        arcpy.Delete_management(outPath + "stie112")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("veje_stier", "", "1", "")
      rasTemp = Con(eucDistTemp < 1.51, 112, 1)
      rasTemp.save(outPath + "stie112")
  
  # 114 - parking areas (park114)
    if parks_114 == 1:
      print "Processing parking areas ..."
      if arcpy.Exists(outPath + "park114"):
        arcpy.Delete_management(outPath + "park114")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("parkering", "", "1", "")
      rasTemp = Con(eucDistTemp < 3.0, 114, 1)
      rasTemp.save(outPath + "park114")
  
  # 115 - dirt roads (spor115)
    if dirtroads_115 == 1:
      print "Processing dirt roads  ..."
      if arcpy.Exists(outPath + "spor115"):
        arcpy.Delete_management(outPath + "spor115")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("veje_spor", "", "1", "")
      rasTemp = Con(eucDistTemp < 2.25, 115, 1)
      rasTemp.save(outPath + "spor115")
  
  # 120 - railway tracks (jern120)
    if railways_120 == 1:
      print "Processing railway tracks ..."
      if arcpy.Exists(outPath + "jern120"):
        arcpy.Delete_management(outPath + "jern120")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("jernbane_brudt", "", "1", "")
      rasTemp = Con(eucDistTemp < 4.5, 120, 1)
      rasTemp.save(outPath + "jern120")
  
   # 122 - Small roads (vu30122)
    if smallroads_122 == 1:
      print "Processing small roads  ..."
      if arcpy.Exists(outPath + "vu30122"):
        arcpy.Delete_management(outPath + "vu30122")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("veje_vu30", "", "1", "")
      rasTemp = Con(eucDistTemp < 1.75, 122, 1)
      rasTemp.save(outPath + "vu30122")
  
   # 125 - Intermediate sized roads (vu60125)
    if mediumroads_125 == 1:
      print "Processing medium sized roads ..."
      if arcpy.Exists(outPath + "vu60125"):
        arcpy.Delete_management(outPath + "vu60125")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("veje_vu60", "", "1", "")
      rasTemp = Con(eucDistTemp < 3.0, 125, 1)
      rasTemp.save(outPath + "vu60125")
  
   # 130 - Large roads (vu90130)
    if largeroads_130 == 1:
      print "Processing large roads ..."
      if arcpy.Exists(outPath + "vu90130"):
        arcpy.Delete_management(outPath + "vu90130")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("veje_vu90", "", "1", "")
      rasTemp = Con(eucDistTemp < 5.0, 130, 1)
      rasTemp.save(outPath + "vu90130")
  
  # 150 - pylons (hjsp150)
    if pylons_150 == 1:
      print "Processing pylons ..."
      if arcpy.Exists(outPath + "hjsp150"):
        arcpy.Delete_management(outPath + "hjsp150")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("hjspmast", "", "1", "")
      rasTemp = Con(eucDistTemp < 1.5, 150, 1)
      rasTemp.save(outPath + "hjsp150")
  
  # 155 - wind turbines (vind155)
    if windturbines_155 == 1:
      print "Processing wind turbines ..."
      if arcpy.Exists(outPath + "vind155"):
        arcpy.Delete_management(outPath + "vind155")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("vindmoel", "", "1", "")
      rasTemp = Con(eucDistTemp < 1.5, 155, 1)
      rasTemp.save(outPath + "vind155")
  
  # 205 - built area - low (lavb205)
    if builtuplow_205 == 1:
      print "Processing built areas (low) ..."
      if arcpy.Exists(outPath + "lavb205"):
        arcpy.Delete_management(outPath + "lavb205")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("lavbebyg", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 205)
      rasTemp.save(outPath + "lavb205")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 210 - built area - high (lavb210)
    if builtuphigh_210 == 1:
      print "Processing built areas (high) ..."
      if arcpy.Exists(outPath + "hojb210"):
        arcpy.Delete_management(outPath + "hojb210")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("hojbebyg", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 210)
      rasTemp.save(outPath + "hojb210")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 215 - city center - (byke205)
    if citycenter_215 == 1:
      print "Processing city center ..."
      if arcpy.Exists(outPath + "byke215"):
        arcpy.Delete_management(outPath + "byke215")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("bykerne", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 215)
      rasTemp.save(outPath + "byke215")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 220 - industry (indu220)
    if industry_220 == 1:
      print "Processing industrial areas ..."
      if arcpy.Exists(outPath + "indu220"):
        arcpy.Delete_management(outPath + "indu220")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("industri", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 220)
      rasTemp.save(outPath + "indu220")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 225 - churchyards (225)
    if churchyard_225 == 1:
      print "Processing churchyards ..."
      if arcpy.Exists(outPath + "kirk225"):
        arcpy.Delete_management(outPath + "kirk225")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("kirkegrd", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 225)
      rasTemp.save(outPath + "kirk225")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 230 - sports fields (230)
    if sportsfields_230 == 1:
      print "Processing sports fields ..."
      if arcpy.Exists(outPath + "sprt230"):
        arcpy.Delete_management(outPath + "sprt230")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("sportanlaeg", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 230)
      rasTemp.save(outPath + "sprt230")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 250 - buildings (bygn250)
    if buildings_250 == 1:
      print "Processing buildings ..."
      if arcpy.Exists(outPath + "bygn250"):
        arcpy.Delete_management(outPath + "bygn250")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("bygning", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 250)
      rasTemp.save(outPath + "bygn250")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 310 - forests (skov310)
    if forests_310 == 1:
      print "Processing forests ..."
      if arcpy.Exists(outPath + "skov310"):
        arcpy.Delete_management(outPath + "skov310")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("skov", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 310)
      rasTemp.save(outPath + "skov310")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 315 - shrubs  (krat315)
    if shrubs_315 == 1:
      print "Processing shrubs ..."
      if arcpy.Exists(outPath + "krat315"):
        arcpy.Delete_management(outPath + "krat315")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("krat_bevoksning", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 315)
      rasTemp.save(outPath + "krat315")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 320 - sand flat - mainly beaches (sand320)
    if sand_320 == 1:
      print "Processing sand flats ..."
      if arcpy.Exists(outPath + "sand320"):
        arcpy.Delete_management(outPath + "sand320")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("sand", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 320)
      rasTemp.save(outPath + "sand320")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 325 - heath land (hede325)
    if heathland_325 == 1:
      print "Processing heath land ..."
      if arcpy.Exists(outPath + "hede325"):
        arcpy.Delete_management(outPath + "hede325")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("hede", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 325)
      rasTemp.save(outPath + "hede325")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 330 - wetland (vaad330)
    if wetland_330 == 1:
      print "Processing wetland ..."
      if arcpy.Exists(outPath + "vaad330"):
        arcpy.Delete_management(outPath + "vaad330")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("vaadomraade", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 330)
      rasTemp.save(outPath + "vaad330")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 355 - protected meadows (eng_355)
    if meadowprotected_355 == 1:
      print "Processing protected meadows ..."
      if arcpy.Exists(outPath + "eng_355"):
        arcpy.Delete_management(outPath + "eng_355")
        print "... deleting existing raster"
      feat_class = "paragraf3"
      feat_layer = "eng_355"
      arcpy.MakeFeatureLayer_management(feat_class,feat_layer)
      arcpy.SelectLayerByAttribute_management(feat_layer, "NEW_SELECTION", '"OBJEKTKODE" = 3055')
      eucDistTemp = EucDistance("eng_355","","1","")
      rasTemp = Con(eucDistTemp < 3, 355, 1)
      rasTemp.save(outPath + "eng_355")
  
  # 360 - protected heath land (hede360)
    if heathlandprotected_360 == 1:
      print "Processing protected heath land ..."
      if arcpy.Exists(outPath + "hede360"):
        arcpy.Delete_management(outPath + "hede360")
        print "... deleting existing raster"
      feat_class = "paragraf3"
      feat_layer = "hede360"
      arcpy.MakeFeatureLayer_management(feat_class,feat_layer)
      arcpy.SelectLayerByAttribute_management(feat_layer, "NEW_SELECTION", '"OBJEKTKODE" = 3060')
      eucDistTemp = EucDistance("hede360","","1","")
      rasTemp = Con(eucDistTemp < 3, 360, 1)
      rasTemp.save(outPath + "hede360")
  
  # 365 - protected swamp 3065 (mose365)
    if bog_365 == 1:
      print "Processing protected swamp ..."
      if arcpy.Exists(outPath + "mose365"):
        arcpy.Delete_management(outPath + "mose365")
        print "... deleting existing raster"
      feat_class = "paragraf3"
      feat_layer = "mose365"
      arcpy.MakeFeatureLayer_management(feat_class,feat_layer)
      arcpy.SelectLayerByAttribute_management(feat_layer, "NEW_SELECTION", '"OBJEKTKODE" = 3065')
      eucDistTemp = EucDistance("mose365","","1","")
      rasTemp = Con(eucDistTemp < 3, 365, 1)
      rasTemp.save(outPath + "mose365")
  
  # 370 - protected dry grassland 3070 (over370)
    if drygrassland_370 == 1:
      print "Processing protected dry grassland ..."
      if arcpy.Exists(outPath + "over370"):
        arcpy.Delete_management(outPath + "over370")
        print "... deleting existing raster"
      feat_class = "paragraf3"
      feat_layer = "over370"
      arcpy.MakeFeatureLayer_management(feat_class,feat_layer)
      arcpy.SelectLayerByAttribute_management(feat_layer, "NEW_SELECTION", '"OBJEKTKODE" = 3070')
      eucDistTemp = EucDistance("over370","","1","")
      rasTemp = Con(eucDistTemp < 3, 370, 1)
      rasTemp.save(outPath + "over370")
  
  # 375 - protected marsh 3075 (seng375)
    if marshprotected_375 == 1:
      print "Processing protected marsh ..."
      if arcpy.Exists(outPath + "seng375"):
        arcpy.Delete_management(outPath + "seng375")
        print "... deleting existing raster"
      feat_class = "paragraf3"
      feat_layer = "seng375"
      arcpy.MakeFeatureLayer_management(feat_class,feat_layer)
      arcpy.SelectLayerByAttribute_management(feat_layer, "NEW_SELECTION", '"OBJEKTKODE" = 3075')
      eucDistTemp = EucDistance("seng375","","1","")
      rasTemp = Con(eucDistTemp < 3, 375, 1)
      rasTemp.save(outPath + "seng375")
  
  # 380 - protected lakes 3080 (soe_380)
    if lakesprotected_380 == 1:
      print "Processing protected lakes ..."
      if arcpy.Exists(outPath + "soe_380"):
        arcpy.Delete_management(outPath + "soe_380")
        print "... deleting existing raster"
      feat_class = "paragraf3"
      feat_layer = "soe_380"
      arcpy.MakeFeatureLayer_management(feat_class,feat_layer)
      arcpy.SelectLayerByAttribute_management(feat_layer, "NEW_SELECTION", '"OBJEKTKODE" = 3080')
      eucDistTemp = EucDistance("soe_380","","1","")
      rasTemp = Con(eucDistTemp < 1, 380, 1)
      rasTemp.save(outPath + "soe_380")
  
  # 440 - lakes (soer440)
    if lakes_440 == 1:
      print "Processing lakes ..."
      if arcpy.Exists(outPath + "soer440"):
        arcpy.Delete_management(outPath + "soer440")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("soer", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 440)
      rasTemp.save(outPath + "soer440")
      # arcpy.Delete_management(outPath + "tmpRaster")
  
  # 425/435 - Small streams (0-2.5) (vandloeb_brudt)+ buffer  OBS:  remember to use 'ukendte'
    if smallstreams_435 == 1:
      print "Processing small streams (0 - 2.5 meter)"
      if arcpy.Exists(outPath + "aaer435"):
        arcpy.Delete_management(outPath + "aaer435")
        print "... deleting existing raster"
      if arcpy.Exists(outPath + "aaer425"):
        arcpy.Delete_management(outPath + "aaer425")
        print "... deleting existing raster"
      feat_class = "vandloeb_brudt"
      feat_layer = "aaer415"
      arcpy.MakeFeatureLayer_management(feat_class,feat_layer)
      arcpy.SelectLayerByAttribute_management(feat_layer, "NEW_SELECTION", '"MIT_BREDDE" = \'0 - 2,5 m\'')
      arcpy.SelectLayerByAttribute_management(feat_layer, "ADD_TO_SELECTION", '"MIT_BREDDE" = \'Ukendt\'')
      eucDistTemp = EucDistance("aaer415","","1","")
      rasTemp = Con(eucDistTemp < 0.95, 435, 1)
      rasTemp.save(outPath + "aaer435")
      rasTemp = Con(eucDistTemp < 2.01, 425, 1)
      rasTemp.save(outPath + "aaer425")
  
  # 426/436 - medium streams (2.5-12) (vandloeb_brudt)+ buffer
    if mediumstreams_436 == 1:
      print "Processing medium streams (2.5 - 12 meter)"
      if arcpy.Exists(outPath + "aaer436"):
        arcpy.Delete_management(outPath + "aaer436")
        print "... deleting existing raster"
      if arcpy.Exists(outPath + "aaer426"):
        arcpy.Delete_management(outPath + "aaer426")
        print "... deleting existing raster"
      feat_class = "vandloeb_brudt"
      feat_layer = "aaer416"
      arcpy.MakeFeatureLayer_management(feat_class,feat_layer)
      arcpy.SelectLayerByAttribute_management(feat_layer, "NEW_SELECTION", '"MIT_BREDDE" = \'2,5 - 12 m\'')
      eucDistTemp = EucDistance("aaer416","","1","")
      rasTemp = Con(eucDistTemp < 5, 436, 1)
      rasTemp.save(outPath + "aaer436")
      rasTemp = Con(eucDistTemp < 7, 426, 1)
      rasTemp.save(outPath + "aaer426")
  
  # 427/437 - large streams (> 12 meter) (vandloeb_brudt)+ buffer
    if largestreams_437 == 1:
      print "Processing large streams (> 12 meter)"
      if arcpy.Exists(outPath + "aaer437"):
        arcpy.Delete_management(outPath + "aaer437")
        print "... deleting existing raster"
      if arcpy.Exists(outPath + "aaer427"):
        arcpy.Delete_management(outPath + "aaer427")
        print "... deleting existing raster"
      feat_class = "vandloeb_brudt"
      feat_layer = "aaer417"
      arcpy.MakeFeatureLayer_management(feat_class,feat_layer)
      arcpy.SelectLayerByAttribute_management(feat_layer, "NEW_SELECTION", '"MIT_BREDDE" = \'over 12 m\'')
      eucDistTemp = EucDistance("aaer417","","1","")
      rasTemp = Con(eucDistTemp < 5, 437, 1)
      rasTemp.save(outPath + "aaer437")
      rasTemp = Con(eucDistTemp < 7, 427, 1)
      rasTemp.save(outPath + "aaer427")
  
  # 420 - lake buffer zones (soer410)
    if lakebuffer_420 == 1:
      print "Processing lake buffer zones  ..."
      if arcpy.Exists(outPath + "sorn420"):
        arcpy.Delete_management(outPath + "sorn420")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("soer","","1","")
      rasTemp = Con(eucDistTemp < 2.05, 420, 1)
      rasTemp.save(outPath + "sorn420")
  
  # mark1000 plus - converts field polygons and assign each polygon a unique id
    if fields_1000 == 1:
      print "Processing field polygons ..."
      if arcpy.Exists(outPath + "mark1000"):
        arcpy.Delete_management(outPath + "mark1000")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("MarkerDK2013", "markpolyID", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      markNummerFirst = (Plus(outPath + "tmpRaster", 0))
      markNummer = Int(markNummerFirst)
      rasTemp = Con(rasIsNull == 1, 1, markNummer)
      rasTemp.save(outPath + "mark1000")
     # arcpy.Delete_management(outPath + "tmpRaster")
  
  # 620 - dikes (dige620)
    if dikes_620 == 1:
      print "Processing dikes ..."
      if arcpy.Exists(outPath + "dige620"):
        arcpy.Delete_management(outPath + "dige620")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("dige", "", "1", "")
      rasTemp = Con(eucDistTemp < 1.2, 620, 1)
      rasTemp.save(outPath + "dige620")
  
  # 625 - archeological sites (fred625)
    if archeological_625 == 1:
      print "Processing ancient cultural trails ..."
      if arcpy.Exists(outPath + "fred625"):
        arcpy.Delete_management(outPath + "trae640")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("fred_fortid", "", "1", "")
      rasTemp = Con(eucDistTemp < 6, 625, 1)
      rasTemp.save(outPath + "fred625")
  
  # 630 - recreational areas (rekr630)
    if recreational_630 == 1:
      print "Processing recreational areas ..."
      if arcpy.Exists(outPath + "rekr630"):
        arcpy.Delete_management(outPath + "rekr630")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("rekromr", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 630)
      rasTemp.save(outPath + "rekr630")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 635 - hedgerows (hegn635)
    if hedgerows_635 == 1:
      print "Processing hedgerows..."
      if arcpy.Exists(outPath + "hegn635"):
        arcpy.Delete_management(outPath + "hegn635")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("hegn", "", "1", "")
      rasTemp = Con(eucDistTemp < 2, 635, 1)
      rasTemp.save(outPath + "hegn635")
  
  # 640 - coppice/tree groups (trae640)
    if coppice_640 == 1:
      print "Processing tree groups ..."
      if arcpy.Exists(outPath + "trae640"):
        arcpy.Delete_management(outPath + "trae640")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("traegruppe", "", "1", "")
      rasTemp = Con(eucDistTemp < 8, 640, 1)
      rasTemp.save(outPath + "trae640")
  
  # 641 - individual trees (trae641)
    if individualtrees_641 == 1:
      print "Processing individual trees ..."
      if arcpy.Exists(outPath + "trae641"):
        arcpy.Delete_management(outPath + "trae641")
        print "... deleting existing raster"
      eucDistTemp = EucDistance("trae", "", "1", "")
      rasTemp = Con(eucDistTemp < 4, 641, 1)
      rasTemp.save(outPath + "trae641")
  
  # 650- gravel pits (raas650)
    if gravelpits_650 == 1:
      print "Processing gravel pits ..."
      if arcpy.Exists(outPath + "raas650"):
        arcpy.Delete_management(outPath + "raas650")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("raastof", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, 650)
      rasTemp.save(outPath + "raas650")
      arcpy.Delete_management(outPath + "tmpRaster")
  
  # 1100- AIS map (ais1100)
    if ais_1100 == 1:
      print "Processing AIS map ..."
      if arcpy.Exists(outPath + "ais1100"):
        arcpy.Delete_management(outPath + "ais1100")
        print "... deleting existing raster"
      arcpy.PolygonToRaster_conversion("ais100", "LUATYPE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
      rasIsNull = IsNull(outPath + "tmpRaster")
      rasTemp = Con(rasIsNull == 1, 1, outPath + "tmpRaster")
      rasTemp.save(outPath + "ais1100")
      arcpy.Delete_management(outPath + "tmpRaster")
  
    rasTemp = ''
    print " "
  #===== End Chunk: Conversion =====#
  
  #===== Chunk: Themes =====#
  # Combine rasters to thematic maps 
  
    if Road == 1:   #Assembles a transportation theme for roads and road verges
      print "Processing road theme ..."
      if arcpy.Exists(outPath + "T1_road"):
        arcpy.Delete_management(outPath + "T1_road")
        print "... deleting existing raster"
      rasterList = [Raster (outPath + "vejk110"), Raster (outPath + "stie112"), Raster (outPath + "spor115"), Raster (outPath + "hjsp150"), Raster (outPath + "vind155"),
                     Raster (outPath + "jern120"), Raster (outPath + "vu30122"), Raster (outPath + "vu60125"), Raster (outPath + "vu90130"), Raster (outPath + "park114"),
                      Raster(outPath + "landhav")]
      rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
      rasTemp.save (outPath + "T1_road")
  
    if builtup == 1:   #Assembles a built up theme
      print "Processing built up theme..."
      if arcpy.Exists(outPath + "T2_building"):
        arcpy.Delete_management(outPath + "T2_building")
        print "... deleting existing raster"
      rasterList = [Raster (outPath + "lavb205"), Raster (outPath + "hojb210"), Raster (outPath + "byke215"), Raster (outPath + "kirk225"), Raster (outPath + "bygn250"),
       Raster (outPath + "sprt230"), Raster (outPath + "indu220"), Raster (outPath + "landhav")]
      rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
      rasTemp.save (outPath + "T2_building")
  
    if nature == 1:   #Assembles a natural areas theme
      print "Processing natural areas ..."
      if arcpy.Exists(outPath + "T3_nature"):
        arcpy.Delete_management(outPath + "T3_nature")
        print "... deleting existing raster"
      rasterList = [Raster (outPath + "skrt105"), Raster (outPath + "skov310"), Raster (outPath + "krat315"), Raster (outPath + "sand320"), Raster (outPath + "hede325"), 
      Raster (outPath + "vaad330"), Raster (outPath + "eng_355"), Raster (outPath + "hede360"), Raster (outPath + "mose365"), Raster (outPath + "over370"), Raster (outPath + "seng375"), 
      Raster (outPath + "soe_380"), Raster (outPath + "landhav")]
      rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
      rasTemp.save (outPath + "T3_nature")
  
    if wetnature == 1:   #Assembles a 'wet nature' theme
      print "Processing wet natural areas ..."
      if arcpy.Exists(outPath + "T3_wetnature"):
        arcpy.Delete_management(outPath + "T3_wetnature")
        print "... deleting existing raster"
      rasterList = [Raster (outPath + "mose365"), Raster (outPath + "soe_380"), Raster (outPath + "landhav")]
      rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
      rasTemp.save (outPath + "T3_wetnature")
  
    if freshwater == 1:   #Assembles a fresh water theme
      print "Processing streams and lakes ..."
      if arcpy.Exists(outPath + "T4_water"):
        arcpy.Delete_management(outPath + "T4_water")
        print "... deleting existing raster"
      rasterList = [Raster (outPath + "soer440"), Raster (outPath + "aaer435"), Raster (outPath + "aaer436"), Raster (outPath + "aaer437"),
                      Raster (outPath + "sorn420"), Raster (outPath + "aaer425"), Raster (outPath + "aaer426"), Raster (outPath + "aaer427"), Raster (outPath + "landhav")]
      rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
      rasTemp.save (outPath + "T4_water")
  
  
    if cultural == 1:   # Assembles a theme o cultural features
      print "Processing hedgerows, dikes, trees, etc ..."
      if arcpy.Exists(outPath + "T5_culture"):
        arcpy.Delete_management(outPath + "T5_culture")
        print "... deleting existing raster"
      rasterList = [Raster (outPath + "dige620"), Raster (outPath + "fred625"), Raster (outPath + "rekr630"), Raster (outPath + "hegn635"), Raster (outPath + "trae640"), 
      Raster (outPath + "trae641"), Raster (outPath + "raas650"), Raster (outPath + "landhav")]
      rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
      rasTemp.save (outPath + "T5_culture")
  #===== End Chunk: Themes =====#
  
  #===== Chunk: Stack =====#
  # Assemble the final map
  # First delete any existing layers
    if finalmap == 1:   
      print "Processing mosaic for all themes ..."
      if arcpy.Exists(outPath + "MapReclassified"):
        arcpy.Delete_management(outPath + "MapReclassified")
        print "... deleting existing raster"
      if arcpy.Exists(outPath + "MapRaw"):
        arcpy.Delete_management(outPath + "MapRaw")
        print "... deleting existing raster"
      if arcpy.Exists(outPath + "MapFinal"):
        arcpy.Delete_management(outPath + "MapFinal")
        print "... deleting existing raster"
  
      print " "
  
   # Stack the thematic maps 
   # Here the hierarchy of individual themes is determined
      T1ve = Raster(outPath + "T1_road")
      T2be = Raster(outPath + "T2_building")
      T3na = Raster(outPath + "T3_nature")
      T3ana = Raster(outPath + "T3_wetnature")
      T4va = Raster(outPath + "T4_water")
      T5ku = Raster(outPath + "T5_culture")
      ais1100 = Raster(outPath + "ais_1100")
      field = Raster(outPath + "fields_1000")   # fields
      landsea = Raster(outPath + "landhav")
      buildings_250 = Raster(outPath + "bygn250")
  
      step1 = Con(field > 999, field, 1)                    # fields first
      print "fields added to map ..."
      step2 = Con(T4va == 1, step1, T4va)                   # freshwater on top
      print "fresh water added to map ..."
      step3 = Con(step2 == 1, T3na, step2)                  # natural areas on NOT (fields, water)
      print "natural areas added to map ..."
      step4 = Con(step3 == 1, T2be, step3)                  # built up areas on NOT (fields, water, natural areas)
      print "built up areas added to map ..."
      step4a = Con(T3ana == 1, step4, T3ana)                # wet natural areas on top
      print "wet natural areas added to map  ..."
      step5 = Con(T5ku == 1, step4a, T5ku)                  # cultural features on top
      print "cultural landscape features added to map ..."
      step6 = Con(T1ve == 1, step5, T1ve)                   # roads on top
      print "roads added to map ..."
      step7 = Con(buildings_250 == 1, step6, buildings_250)                   # buildings on top
      print "buildings added to map ..."
      map01 = Con(landhav == 1, step7, 0)                # sea added
      print "sea added to map ..."
      map1 = Con(map01 == 1, ais1100, map01) # Use the AIS layer if a cell was not filled by any of the layers above.
      map1.save (outPath + "MapRaw")
      nowTime = time.strftime('%X %x')
      print "Raw map assembled ..." + nowTime
      print "  "
  #===== End Chunk: Stack =====#
  
  #===== Chunk: Finalize =====#
  # Reclassify to ALMaSS raster values
  # ALMaSS uses different values for the landcover types, so this step simply translates
  # the numeric values.
      mosaik2 = ReclassByASCIIFile(map1, reclasstable, "DATA")
      mosaik2.save(outPath + "MapReclassified")
      nowTime = time.strftime('%X %x')
      print "Reclassification done ..." + nowTime
  
  # regionalise map
      regionALM = RegionGroup(mosaik2,"EIGHT","WITHIN","ADD_LINK","")
      regionALM.save(outPath + "MapFinal")
      nowTime = time.strftime('%X %x')
      print "Regionalisation done ..." + nowTime
  
  # convert regionalised map to ascii
      arcpy.RasterToASCII_conversion(regionALM, asciiexp)
      print "Conversion to ASCII done ..." + nowTime
  
    endTime = time.strftime('%X %x')
    print ""
    print "Landscape generated: " + endTime
  
#===== End Chunk: Finalize =====#



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
