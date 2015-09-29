# Looping through the landscapes
# Snippet to set up directory structure and copy files into it
# Date Sep 29 2015
# Author: Lars Dalby

import shutil, os

# Names of the new landscapes
NJ = ['NJ1', 'NJ2', 'NJ3', 'NJ4', 'NJ5', 'NJ6']
VJ = ['VJ1', 'VJ2', 'VJ3', 'VJ4', 'VJ5']
OJ = ['OJ1', 'OJ2', 'OJ3', 'OJ4']
FU = ['FU1', 'FU2', 'FU3', 'FU4']
NS = ['NS1', 'NS2', 'NS3', 'NS4']
SS = ['SS1', 'SS2', 'SS3', 'SS4', 'SS5', 'SS6']

landscapes = NJ + VJ + OJ + FU + NS + SS
landscapes.append("BO1")

# Path to the template directory:
template = "c:/Users/lada/Desktop/Skabelon/"

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
outPath = os.path.join(dst,landscapes[index] + ".gdb")
gisDB = "O:/ST_LandskabsGenerering/gis/dkgis.gdb"                                             # input features
scratchDB = os.path.join(dst,landscapes[index], "scratch")                      # scratch folder for tempfiles
asciifile = "ASCII_" + landscapes[index] + ".txt"
asciiexp = os.path.join(dst,landscapes[index], asciifile)              # export in ascii (for ALMaSS)
reclasstable = os.path.join(dst, landscapes[index], "reclass.txt")               # re
# Select the landscape and convert to raster
mask = os.path.join(dst, landscapes[index] + "/project.gdb/mask")
arcpy.PolygonToRaster_conversion("shapefilename", landscapes[index], mask, "CELL_CENTER", "NONE", "1")
localSettings = os.path.join(dst, landscapes[index], "project.gdb/mask"   # project folder with mask