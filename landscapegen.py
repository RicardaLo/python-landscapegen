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
localSettings = "O:/ST_LandskabsGenerering/outputs/kvadrater/haslev/project.gdb/haslevmask"   # project folder with mask
gisDB = "c:/Users/lada/Landskabsgenerering/Norge/norwaygis.gdb"                    # input features
scratchDB = "c:/Users/lada/Landskabsgenerering/Norge/scratch"                      # scratch folder for tempfiles
asciiexp = "c:/Users/lada/Landskabsgenerering/Norge/ASCII_haslev.txt"              # export in ascii (for ALMaSS)
reclasstable = "c:/Users/lada/Landskabsgenerering/Norge/reclass.txt"               # reclass ascii table

# MODEL SETTINGS
arcpy.env.overwriteOutput = True
arcpy.env.workspace = gisDB
arcpy.env.scratchWorkspace = scratchDB
arcpy.env.extent = localSettings
arcpy.env.mask = localSettings
arcpy.env.cellSize = localSettings
print "... model settings read"

# MODEL EXECUTION - controls which processes are executed

default = 1  # 1 -> run process; 0 -> not run process

#MOSAIC
vejnet_c = default      #create road theme
bebyggelser_c = default #create built up theme
natur_c = default       #create nature theme
vaadnatur_c = default   #create wet nature theme
ferskvand_c = default   #create fresh water theme
kultur_c = default      #create culturral feature theme
mosaik_c = default      #assemble final mosaic

#CONVERSION  - features to raster layers
landhav_c = default   #land_sea
skrt105_c = default   #slopes along roads
vejk110_c = default   #road verges
stie112_c = default   #paths
park114_c = default   #parking areas
spor115_c = default   #unpaved roads and tracks
jern120_c = default   #railways
vu30122_c = default   #small roads (< 3 meter)
vu60125_c = default   #medium sized roads (3-6 meter)
vu90130_c = default   #large roads (> 6 meter)
hjsp150_c = default   #pylons
vind155_c = default   #wind turbines
lavb205_c = default   #built up areas low
hojb210_c = default   #built up areas high
byke215_c = default   #city center
indu220_c = default   #industrial areas
kirk225_c = default   #cemeteries
sprt230_c = default   #sports areas
bygn250_c = default   #buildings
skov310_c = default   #top10dk forest
krat315_c = default   #top10dk shrub
sand320_c = default   #top10dk sand flats
hede325_c = default   #top10dk heath land
vaad330_c = default   #top10dk wetland
eng_355_c = default   #protected meadows
hede360_c = default   #protected heath land
mose365_c = default   #protected bog
over370_c = default   #protected dry grassland
seng375_c = default   #protected salt marshes
soe_380_c = default   #protected lakes
soer440_c = default   #lakes
aaer435_c = default   #small streams (< 2.5 meter)
aaer436_c = default   #medium streams (2.5 - 12 meter)
aaer437_c = default   #large streams (> 12 meter)
sorn420_c = default   #lake buffer
mark1000_c = default  #fields
dige620_c = default   #dikes
fred625_c = default   #archeological sites
rekr630_c = default   #recreational areas
hegn635_c = default   #hedgerows
trae640_c = default   #tree groups
trae641_c = default   #individual trees
raas650_c = default   #gravel pits
ais1100_c = default   #ais landcover map

#NB: these buffers are calculated automatically - mentioned here to keep track on codes
#aarn425    #buffers small streams
#aarn426    #buffers medium streams
#aarn427    #buffers large streams

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
    arcpy.PolygonToRaster_conversion("T32_1702vann_flate", "POLY", outPath + "Water", "CELL_CENTER", "NONE", "1")







# 105 - slopes along larger roads (skrt105)
  if skrt105_c == 1:
    print "Processing artificial slopes along larger roads ..."
    if arcpy.Exists(outPath + "skrt105"):
      arcpy.Delete_management(outPath + "skrt105")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("skraent","","1","")
    rasTemp = Con(eucDistTemp < 2.5, 105, 1)
    rasTemp.save(outPath + "skrt105")

# 110 - road verges (vejk110)
  if vejk110_c == 1:
    print "Processing road verges ..."
    if arcpy.Exists(outPath + "vejk110"):
      arcpy.Delete_management(outPath + "vejk110")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("vejkant","","1","")
    rasTemp = Con(eucDistTemp < 1.75, 110, 1)
    rasTemp.save(outPath + "vejk110")

# 112 - paths (stie112)
  if stie112_c == 1:
    print "Processing paths  ..."
    if arcpy.Exists(outPath + "stie112"):
      arcpy.Delete_management(outPath + "stie112")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("veje_stier", "", "1", "")
    rasTemp = Con(eucDistTemp < 1.51, 112, 1)
    rasTemp.save(outPath + "stie112")

# 114 - parking areas (park114)
  if park114_c == 1:
    print "Processing parking areas ..."
    if arcpy.Exists(outPath + "park114"):
      arcpy.Delete_management(outPath + "park114")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("parkering", "", "1", "")
    rasTemp = Con(eucDistTemp < 3.0, 114, 1)
    rasTemp.save(outPath + "park114")

# 115 - dirt roads (spor115)
  if spor115_c == 1:
    print "Processing dirt roads  ..."
    if arcpy.Exists(outPath + "spor115"):
      arcpy.Delete_management(outPath + "spor115")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("veje_spor", "", "1", "")
    rasTemp = Con(eucDistTemp < 2.25, 115, 1)
    rasTemp.save(outPath + "spor115")

# 120 - railway tracks (jern120)
  if jern120_c == 1:
    print "Processing railway tracks ..."
    if arcpy.Exists(outPath + "jern120"):
      arcpy.Delete_management(outPath + "jern120")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("jernbane_brudt", "", "1", "")
    rasTemp = Con(eucDistTemp < 4.5, 120, 1)
    rasTemp.save(outPath + "jern120")

 # 122 - Small roads (vu30122)
  if vu30122_c == 1:
    print "Processing small roads  ..."
    if arcpy.Exists(outPath + "vu30122"):
      arcpy.Delete_management(outPath + "vu30122")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("veje_vu30", "", "1", "")
    rasTemp = Con(eucDistTemp < 1.75, 122, 1)
    rasTemp.save(outPath + "vu30122")

 # 125 - Intermediate sized roads (vu60125)
  if vu60125_c == 1:
    print "Processing medium sized roads ..."
    if arcpy.Exists(outPath + "vu60125"):
      arcpy.Delete_management(outPath + "vu60125")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("veje_vu60", "", "1", "")
    rasTemp = Con(eucDistTemp < 3.0, 125, 1)
    rasTemp.save(outPath + "vu60125")

 # 130 - Large roads (vu90130)
  if vu90130_c == 1:
    print "Processing large roads ..."
    if arcpy.Exists(outPath + "vu90130"):
      arcpy.Delete_management(outPath + "vu90130")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("veje_vu90", "", "1", "")
    rasTemp = Con(eucDistTemp < 5.0, 130, 1)
    rasTemp.save(outPath + "vu90130")

# 150 - pylons (hjsp150)
  if hjsp150_c == 1:
    print "Processing pylons ..."
    if arcpy.Exists(outPath + "hjsp150"):
      arcpy.Delete_management(outPath + "hjsp150")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("hjspmast", "", "1", "")
    rasTemp = Con(eucDistTemp < 1.5, 150, 1)
    rasTemp.save(outPath + "hjsp150")

# 155 - wind turbines (vind155)
  if vind155_c == 1:
    print "Processing wind turbines ..."
    if arcpy.Exists(outPath + "vind155"):
      arcpy.Delete_management(outPath + "vind155")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("vindmoel", "", "1", "")
    rasTemp = Con(eucDistTemp < 1.5, 155, 1)
    rasTemp.save(outPath + "vind155")

# 205 - built area - low (lavb205)
  if lavb205_c == 1:
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
  if hojb210_c == 1:
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
  if byke215_c == 1:
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
  if indu220_c == 1:
    print "Processing industrial areas ..."
    if arcpy.Exists(outPath + "indu220"):
      arcpy.Delete_management(outPath + "indu220")
      print "... deleting existing raster"
    arcpy.PolygonToRaster_conversion("industri", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
    rasIsNull = IsNull(outPath + "tmpRaster")
    rasTemp = Con(rasIsNull == 1, 1, 220)
    rasTemp.save(outPath + "indu220")
    arcpy.Delete_management(outPath + "tmpRaster")

# 225 - cemeteries (225)
  if kirk225_c == 1:
    print "Processing cemeteries ..."
    if arcpy.Exists(outPath + "kirk225"):
      arcpy.Delete_management(outPath + "kirk225")
      print "... deleting existing raster"
    arcpy.PolygonToRaster_conversion("kirkegrd", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
    rasIsNull = IsNull(outPath + "tmpRaster")
    rasTemp = Con(rasIsNull == 1, 1, 225)
    rasTemp.save(outPath + "kirk225")
    arcpy.Delete_management(outPath + "tmpRaster")

# 230 - sports fields (230)
  if sprt230_c == 1:
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
  if bygn250_c == 1:
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
  if skov310_c == 1:
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
  if krat315_c == 1:
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
  if sand320_c == 1:
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
  if hede325_c == 1:
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
  if vaad330_c == 1:
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
  if eng_355_c == 1:
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
  if hede360_c == 1:
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
  if mose365_c == 1:
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
  if over370_c == 1:
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
  if seng375_c == 1:
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
  if soe_380_c == 1:
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
  if soer440_c == 1:
    print "Processing lakes ..."
    if arcpy.Exists(outPath + "soer440"):
      arcpy.Delete_management(outPath + "soer440")
      print "... deleting existing raster"
    arcpy.PolygonToRaster_conversion("soer", "FEAT_KODE", outPath + "tmpRaster", "CELL_CENTER", "NONE", "1")
    rasIsNull = IsNull(outPath + "tmpRaster")
    rasTemp = Con(rasIsNull == 1, 1, 440)
    rasTemp.save(outPath + "soer440")
    # arcpy.Delete_management(outPath + "tmpRaster")

# 425/435 - Small streams (2.5-12) (vandloeb_brudt)+ buffer  OBS:  remember to use 'ukendte'
  if aaer435_c == 1:
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
  if aaer436_c == 1:
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
  if aaer437_c == 1:
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
  if sorn420_c == 1:
    print "Processing lake buffer zones  ..."
    if arcpy.Exists(outPath + "sorn420"):
      arcpy.Delete_management(outPath + "sorn420")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("soer","","1","")
    rasTemp = Con(eucDistTemp < 2.05, 420, 1)
    rasTemp.save(outPath + "sorn420")

# mark1000 plus - converts field polygons and assign each polygon a unique id
  if mark1000_c == 1:
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
  if dige620_c == 1:
    print "Processing dikes ..."
    if arcpy.Exists(outPath + "dige620"):
      arcpy.Delete_management(outPath + "dige620")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("dige", "", "1", "")
    rasTemp = Con(eucDistTemp < 1.2, 620, 1)
    rasTemp.save(outPath + "dige620")

# 625 - archeological sites (fred625)
  if fred625_c == 1:
    print "Processing ancient cultural trails ..."
    if arcpy.Exists(outPath + "fred625"):
      arcpy.Delete_management(outPath + "trae640")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("fred_fortid", "", "1", "")
    rasTemp = Con(eucDistTemp < 6, 625, 1)
    rasTemp.save(outPath + "fred625")

# 630 - recreational areas (rekr630)
  if rekr630_c == 1:
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
  if hegn635_c == 1:
    print "Processing hedgerows..."
    if arcpy.Exists(outPath + "hegn635"):
      arcpy.Delete_management(outPath + "hegn635")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("hegn", "", "1", "")
    rasTemp = Con(eucDistTemp < 2, 635, 1)
    rasTemp.save(outPath + "hegn635")

# 640 - tree groups (trae640)
  if trae640_c == 1:
    print "Processing tree groups ..."
    if arcpy.Exists(outPath + "trae640"):
      arcpy.Delete_management(outPath + "trae640")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("traegruppe", "", "1", "")
    rasTemp = Con(eucDistTemp < 8, 640, 1)
    rasTemp.save(outPath + "trae640")

# 641 - individual trees (trae641)
  if trae641_c == 1:
    print "Processing individual trees ..."
    if arcpy.Exists(outPath + "trae641"):
      arcpy.Delete_management(outPath + "trae641")
      print "... deleting existing raster"
    eucDistTemp = EucDistance("trae", "", "1", "")
    rasTemp = Con(eucDistTemp < 4, 641, 1)
    rasTemp.save(outPath + "trae641")

# 650- gravel pits (raas650)
  if raas650_c == 1:
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
  if ais1100_c == 1:
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

  
# 2) Combine rasters to thematic maps 

  if vejnet_c == 1:   #Assembles a transportation theme for roads and road verges
    print "Processing road theme ..."
    if arcpy.Exists(outPath + "T1_vejnet"):
      arcpy.Delete_management(outPath + "T1_vejnet")
      print "... deleting existing raster"
    rasterList = [Raster (outPath + "vejk110"), Raster (outPath + "stie112"), Raster (outPath + "spor115"), Raster (outPath + "hjsp150"), Raster (outPath + "vind155"),
                   Raster (outPath + "jern120"), Raster (outPath + "vu30122"), Raster (outPath + "vu60125"), Raster (outPath + "vu90130"), Raster (outPath + "park114"),
                    Raster(outPath + "landhav")]
    rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
       #  use next line if the road themes should be shrunk - remember to change 'vejnet' above to 'vejnet0'
       #  may result in 'stripes' or other artificial looking features: @todo: Hvad kan resultere i stripes?
       #  vejnet = Shrink(vejnet0, 1, 1)
    rasTemp.save (outPath + "T1_vejnet")

  if bebyggelser_c == 1:   #Assembles a built up theme
    print "Processing built up theme..."
    if arcpy.Exists(outPath + "T2_bebyggelser"):
      arcpy.Delete_management(outPath + "T2_bebyggelser")
      print "... deleting existing raster"
    rasterList = [Raster (outPath + "lavb205"), Raster (outPath + "hojb210"), Raster (outPath + "byke215"), Raster (outPath + "kirk225"), Raster (outPath + "bygn250"),
     Raster (outPath + "sprt230"), Raster (outPath + "indu220"), Raster (outPath + "landhav")]
    rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
    rasTemp.save (outPath + "T2_bebyggelser")

  if vaadnatur_c == 1:   #Assembles a 'wet nature' theme
    print "Processing wet natural areas ..."
    if arcpy.Exists(outPath + "T3_vaadnatur"):
      arcpy.Delete_management(outPath + "T3_vaadnatur")
      print "... deleting existing raster"
    rasterList = [Raster (outPath + "mose365"), Raster (outPath + "soe_380"), Raster (outPath + "landhav")]
    rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
    rasTemp.save (outPath + "T3_vaadnatur")

  if ferskvand_c == 1:   #Assembles a fresh water theme
    print "Processing streams and lakes ..."
    if arcpy.Exists(outPath + "T4_vand"):
      arcpy.Delete_management(outPath + "T4_vand")
      print "... deleting existing raster"
    rasterList = [Raster (outPath + "soer440"), Raster (outPath + "aaer435"), Raster (outPath + "aaer436"), Raster (outPath + "aaer437"),
                    Raster (outPath + "sorn420"), Raster (outPath + "aaer425"), Raster (outPath + "aaer426"), Raster (outPath + "aaer427"), Raster (outPath + "landhav")]
    rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
    rasTemp.save (outPath + "T4_vand")

  if natur_c == 1:   #Assembles a natural areas theme
    print "Processing natural areas ..."
    if arcpy.Exists(outPath + "T3_natur"):
      arcpy.Delete_management(outPath + "T3_natur")
      print "... deleting existing raster"
    rasterList = [Raster (outPath + "skrt105"), Raster (outPath + "skov310"), Raster (outPath + "krat315"), Raster (outPath + "sand320"), Raster (outPath + "hede325"), 
    Raster (outPath + "vaad330"), Raster (outPath + "eng_355"), Raster (outPath + "hede360"), Raster (outPath + "mose365"), Raster (outPath + "over370"), Raster (outPath + "seng375"), 
    Raster (outPath + "soe_380"), Raster (outPath + "landhav")]
    rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
    rasTemp.save (outPath + "T3_natur")

  if kultur_c == 1:   # Assembles a theme of cultural features
    print "Processing hedgerows, dikes, trees, etc ..."
    if arcpy.Exists(outPath + "T5_kultur"):
      arcpy.Delete_management(outPath + "T5_kultur")
      print "... deleting existing raster"
    rasterList = [Raster (outPath + "dige620"), Raster (outPath + "fred625"), Raster (outPath + "rekr630"), Raster (outPath + "hegn635"), Raster (outPath + "trae640"), 
    Raster (outPath + "trae641"), Raster (outPath + "raas650"), Raster (outPath + "landhav")]
    rasTemp = CellStatistics(rasterList, "MAXIMUM", "DATA")
    rasTemp.save (outPath + "T5_kultur")

# Assemble the raw map
# First delete any existing layers
  if mosaik_c == 1:   
    print "Processing mosaic for all themes ..."
    if arcpy.Exists(outPath + "Mosaik_rekl"):
      arcpy.Delete_management(outPath + "Mosaik_rekl")
      print "... deleting existing raster"
    if arcpy.Exists(outPath + "Mosaik_raa"):
      arcpy.Delete_management(outPath + "Mosaik_raa")
      print "... deleting existing raster"
    if arcpy.Exists(outPath + "Mosaik_almass"):
      arcpy.Delete_management(outPath + "Mosaik_almass")
      print "... deleting existing raster"

    print " "

 # 3) Stack the thematic maps 
 # The raw map is put together here.  Here the hierarchy of individual themes is determined
    T1ve = Raster(outPath + "T1_vejnet")
    T2be = Raster(outPath + "T2_bebyggelser")
    T3na = Raster(outPath + "T3_natur")
    T3ana = Raster(outPath + "T3_vaadnatur")
    T4va = Raster(outPath + "T4_vand")
    T5ku = Raster(outPath + "T5_kultur")
    ais1100 = Raster(outPath + "ais1100")
    mark = Raster(outPath + "mark1000")   # fields
    landhav = Raster(outPath + "landhav")
    bygn = Raster(outPath + "bygn250")

    step1 = Con(mark > 999, mark, 1)                    # fields first
    print "fields added to mosaic ..."
    step2 = Con(T4va == 1, step1, T4va)                   # freshwater on top
    print "fresh water added to mosaic ..."
    step3 = Con(step2 == 1, T3na, step2)                  # natural areas on NOT (fields, water)
    print "natural areas added to mosaic ..."
    step4 = Con(step3 == 1, T2be, step3)                  # built up areas on NOT (fields, water, natural areas)
    print "built up areas added to mosaic ..."
    step4a = Con(T3ana == 1, step4, T3ana)                # wet natural areas on top
    print "wet natural areas added to mosaic  ..."
    step5 = Con(T5ku == 1, step4a, T5ku)                  # cultural features on top
    print "cultural landscape features added to mosaic ..."
    step6 = Con(T1ve == 1, step5, T1ve)                   # roads on top
    print "roads added to mosaic ..."
    step7 = Con(bygn == 1, step6, bygn)                   # buildings on top
    print "buildings added to mosaic ..."
    mosaik01 = Con(landhav == 1, step7, 0)                # sea added
    print "sea added to mosaic ..."
    mosaik1 = Con(mosaik01 == 1, ais1100, mosaik01) # Use the AIS layer if a cell was not filled by any of the layers above.
    mosaik1.save (outPath + "Mosaik_raa")
    nowTime = time.strftime('%X %x')
    print "Raw mosaic assembled ..." + nowTime
    print "  "

# Reclassify to ALMaSS raster values
# ALMaSS uses different values for the landcover types, so this step simply translates
# the numeric values.
    mosaik2 = ReclassByASCIIFile(mosaik1, reclasstable, "DATA")
    mosaik2.save(outPath + "Mosaik_rekl")
    nowTime = time.strftime('%X %x')
    print "Reclassification done ..." + nowTime

# regionalise map
    regionALM = RegionGroup(mosaik2,"EIGHT","WITHIN","ADD_LINK","")
    regionALM.save(outPath + "Mosaik_almass")
    nowTime = time.strftime('%X %x')
    print "Regionalisation done ..." + nowTime

# convert regionalised map to ascii
    arcpy.RasterToASCII_conversion(regionALM, asciiexp)
    print "Conversion to ASCII done ..." + nowTime

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
