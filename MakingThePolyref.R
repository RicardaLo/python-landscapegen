# Making the polyref 
# Date: 28 November 2014
# Author: Lars Dalby

# This script will generate the polyref file almass needs
# You need to export the attribute table for your landscape
# first. 


if(!require(ralmass)) 
{
	library(devtools)
	install_github('LDalby/ralmass')
}
library(ralmass)
library(data.table)

PathToFile = 'o:/ST_LandskabsGenerering/outputs/kvadrater/kolding/'  # The attribute table from NAME_almass. It needs to be exported from ArcGIS.
LandscapeName = 'Kolding'
FileName = paste(LandscapeName, 'Attr.txt', sep = '')
attr = fread(paste(PathToFile, FileName, sep = ''))
cleanattr = CleanAttrTable(AttrTable = attr, Soiltype = TRUE)  # see ?CleanAttrTable for documentation
dim(cleanattr)
setkey(cleanattr, 'PolyType')
targetfarms = cleanattr[PolyType >= 10000]  # Get the fields
targetfarms[,Soiltype:=NULL]
cleanattr = cleanattr[PolyType < 10000]  # Get the rest
dim(cleanattr)
str(targetfarms)


# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
#	    			The farm info  						   #
# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
# Here we get the merge farminformation back onto the markpolyID:
farm = fread('o:/ST_LandskabsGenerering/outputs/FarmInfo2013.txt')
farminfo = farm[, c('AlmassCode', 'markpolyID', 'BedriftID', 'BedriftPlusID', 'AfgKode'), with = FALSE]  # Extract only the columns we need for now
farminfo[,markpolyID:= gsub(pattern = ',', replacement = '', x = farminfo$markpolyID, fixed = FALSE)]  # Fix seperator issue
farminfo[,markpolyID:= as.numeric(farminfo$markpolyID)]
setkey(farminfo, 'markpolyID')

unique(farminfo[, AlmassCode])  # Issue with #N/A and type 59 (old code)
farminfo[AlmassCode == '#N/A', AlmassCode:='20',]  # If no info, we assign field
farminfo[AlmassCode == '59',AlmassCode:='216']  # Translate to the new code
farminfo[AlmassCode == '71',AlmassCode:='214']  # Translate to the new code
farminfo[,AlmassCode:= as.numeric(farminfo$AlmassCode)]
unique(farminfo[, AlmassCode])  # Okay.

# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
#	    			The soil info  						   #
# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
soil = fread('o:/ST_LandskabsGenerering/gis/GIS_original_data/Jordartskort/markpoly_jordtype.txt')
soil = soil[, c('markpolyID', 'MAJORITY'), with = FALSE]
soil[,markpolyID:= gsub(pattern = ',', replacement = '', x = soil$markpolyID, fixed = FALSE)]
soil[,markpolyID:= as.numeric(soil$markpolyID)]
setnames(soil, old = 'MAJORITY', new = 'Soiltype')
setkey(soil, 'markpolyID')
unique(soil[, Soiltype])  # Looks okay

# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
#	    			Merge soil and farm  				   #
# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #

SnF = merge(farminfo, soil, all.x = TRUE)
SnF[is.na(Soiltype)]  # Some polygons didn't get a soiltype. Assign something else:
# If you want to assign the most frequent type in DK use the following two lines:
# Otherwise we assign a code we can recognize and check further down if any of these
# are in the target landscape.
# TheMostFrequent = as.numeric(names(table(SnF[,Soiltype])[which(table(SnF[,Soiltype]) == max(table(SnF[,Soiltype])))]))
# SnF[is.na(Soiltype), Soiltype:=TheMostFrequent,]
SnF[is.na(Soiltype), Soiltype:=999,]
SnF[, BedriftPlusID:=NULL]
SnF[, AfgKode:=NULL]
SnF[,BedriftID:= gsub(pattern = ',', replacement = '', x = SnF$BedriftID, fixed = FALSE)]
SnF[,BedriftID:= as.numeric(SnF$BedriftID)]

# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
#	 Insert almasscode and soiltype the right places 	   #
# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
setnames(SnF, old = 'markpolyID', new =  'PolyType')  # Quick fix for an easier merge
setkey(SnF, 'PolyType')

temp = merge(x = targetfarms, y = SnF, all.x = TRUE)  # Okay, now we just need to move around a bit
temp[,PolyType:=AlmassCode]
temp[,AlmassCode:=NULL]
temp[,Farmref:=BedriftID]
temp[,BedriftID:=NULL]

result = rbind(cleanattr, temp)  # This is essentially putting the fields and everything else back together.
999 %in% unique(result[, Soiltype])  # Should be false (otherwise you need to decide what to do where fields have no soil type)

# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
#	 Check and clean out farmrefs to types that shouldn't have one 	   #
# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #

result[PolyType == 12, Farmref:=-1]  # AmenityGrass should not have a Farmref
result[PolyType == 110, Farmref:=-1]  # NaturalGrass should not have a Farmref
unique(farminfo[, AlmassCode])  # Okay.

dim(result) 
dim(attr)  # Okay.
setkey(result, 'PolyRefNum')
FileName = paste(LandscapeName, 'PolyRef.txt', sep = '')  # The name of the polyref file
WritePolyref(Table = result, PathToFile = paste(PathToFile, FileName, sep = ''))  # see ?WritePolyref for docu.

# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
#			 Make a small farmref file to go with the landscape 		#
# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #
farm = fread('o:/ST_LandskabsGenerering/outputs/The2013Farmref_UsrDefFarmNumFix.txt')
setnames(farm, c('Farmref', 'FarmType'))
landscapefarms = farm[Farmref %in% unique(result[,Farmref]),]
FileName = paste(LandscapeName, 'Farmref.txt', sep = '')  # The name of the farmref file
WritePolyref(Table = landscapefarms, PathToFile = paste(PathToFile, FileName, sep = ''), Headers = FALSE, Type = 'Farm')  # see ?WritePolyref for docu.

