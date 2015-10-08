# Making the farmref file
# Date: 28-11-2014
# Author: Lars Dalby

if(!require(ralmass)) 
{
	library(devtools)
	install_github('LDalby/ralmass')
}
library(ralmass)
library(data.table)

# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #

farm = fread('o:/ST_LandskabsGenerering/outputs/FarmInfo2013.txt')  # See ???? for documentation of the steps from raw data to this file...

The2013Farmref = farm[, c('BedriftID', 'FarmType'), with = FALSE]
dim(The2013Farmref)  #  619112      2
The2013Farmref = unique(The2013Farmref)
dim(The2013Farmref)  # 38812     2
The2013Farmref[,BedriftID:= gsub(pattern = ',', replacement = '', x = The2013Farmref$BedriftID, fixed = FALSE)]  # Fixing the comma sep issue
The2013Farmref[,BedriftID:= as.numeric(The2013Farmref$BedriftID)]  # Potentially risky...
The2013Farmref[,FarmType:=FarmType+32]  # The first user defined farm number is 33
setkey(The2013Farmref, 'BedriftID')

path ='o:/ST_LandskabsGenerering/outputs/The2013Farmref_UsrDefFarmNumFix.txt'
WritePolyref(Table = The2013Farmref, PathToFile = path, Type = 'Farm')  #See ?WritePolyref for documentation.

# ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ #