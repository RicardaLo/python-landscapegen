# Making the Ref files
# Date: 7 Oct 2015
# Author: Lars Dalby

# Here we make poly- and farmref files based on the updated method for 
# landscape generation (as of Oct 2015)

if(!require(ralmass)) 
{
	library(devtools)
	install_github('LDalby/ralmass')
}
library(ralmass)
library(data.table)

PathToMaps = 'e:/Gis/HareValidation/'
maps = dir(PathToMaps)
# length(maps)

for (i in seq_along(maps))
{
	LandscapeName = maps[i]
	FileName = paste0('ATTR_', LandscapeName, '.csv', sep = '')
	attr = fread(paste0(PathToMaps, LandscapeName, '/', FileName))
	cleanattr = CleanAttrTable(AttrTable = attr, Soiltype = FALSE)
	setkey(cleanattr, 'PolyType')
	targetfarms = cleanattr[PolyType >= 10000]  # Get the fields
	cleanattr = cleanattr[PolyType < 10000]  # Get the rest

# Get the farm information (polytypes for fields and farmrefs)
	farminfo = fread('o:/ST_LandskabsGenerering/outputs/FarmInfo2013CleanOct2015.csv')
	setnames(farminfo, old = 'markpolyID', new =  'PolyType')  # Quick fix for an easier merge
	setkey(farminfo, 'PolyType')

	temp = merge(x = targetfarms, y = farminfo, all.x = TRUE)  # Okay, now we just need to move around a bit
	temp[, c('PolyType', 'FarmRef'):=NULL]
	setnames(temp, old = c('AlmassCode', 'BedriftID'), new = c('PolyType', 'FarmRef'))
	setcolorder(temp, c('PolyType', 'PolyRefNum', 'Area', 'FarmRef', 'UnSprayedMarginRef'))
	result = rbind(cleanattr, temp)  # This is essentially putting the fields and everything else back together.
	
	result[PolyType == 12, FarmRef:=-1]  # AmenityGrass should not have a Farmref
	result[PolyType == 110, FarmRef:=-1]  # NaturalGrass should not have a Farmref
	setkey(result, PolyRefNum)
# Read in the soil types
	FileName = paste0('SOIL_', LandscapeName, '.csv', sep = '')
	soil = fread(paste0(PathToMaps, LandscapeName, '/', FileName))
	soil = CleanSoilTable(soil)
	result = merge(result, soil, all.x = TRUE)  # Both are keyed...

	setcolorder(result, c('PolyType', 'PolyRefNum', 'Area', 'FarmRef',
		'UnSprayedMarginRef', 'SoilType'))
	FileName = paste0('PolyRef', LandscapeName, '.txt')  # The name of the polyref file
	PathToFile = paste0(PathToMaps, LandscapeName, '/', FileName)
	WritePolyref(Table = result, PathToFile = PathToFile)  # see ?WritePolyref for docu.

# Make a small farmref file to go with the landscape
	farm = fread('o:/ST_LandskabsGenerering/outputs/The2013Farmref.txt', skip = 1)
	setnames(farm, c('FarmRef', 'FarmType'))
	landscapefarms = farm[FarmRef %in% unique(result[,FarmRef]),]
	FileName = paste0('Farmref', LandscapeName, '.txt')  # The name of the farmref file
	PathToFile = paste0(PathToMaps, LandscapeName, '/', FileName)
	WritePolyref(Table = landscapefarms, PathToFile = PathToFile, Headers = FALSE, Type = 'Farm')  # see ?WritePolyref for docu.
	print(i)
}
