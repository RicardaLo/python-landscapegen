# Script to document manipulation of the FarmInfo
# Author: Lars Dalby
# Date: Oct 7 2015
# As we are making many landscapes, doing these manipulations on the fly
# became too time consuming. The file written here is used from now on.

farm = fread('o:/ST_LandskabsGenerering/outputs/FarmInfo2013.txt')
columns = c('AlmassCode', 'markpolyID', 'BedriftID', 'BedriftPlusID', 'AfgKode')
farminfo = farm[, columns, with = FALSE]  # Extract only the columns we need for now
farminfo[, markpolyID:=gsub(pattern = ',', replacement = '', x = farminfo$markpolyID, fixed = FALSE)]
farminfo[, markpolyID:=as.numeric(markpolyID)]
farminfo[, BedriftID:=gsub(pattern = ',', replacement = '', x = farminfo$BedriftID, fixed = FALSE)]
farminfo[, BedriftID:=as.numeric(BedriftID)]
unique(farminfo[, AlmassCode])  # Issue with #N/A and type 59 (old code)
farminfo[AlmassCode == '#N/A', AlmassCode:='20',]  # If no info, we assign field
farminfo[AlmassCode == '59',AlmassCode:='216']  # Translate to the new code
farminfo[AlmassCode == '71',AlmassCode:='214']  # Translate to the new code
farminfo[,AlmassCode:= as.numeric(farminfo$AlmassCode)]
unique(farminfo[, AlmassCode])  # Check that these are valid ALMaSS codes only
farminfo[, c('BedriftPlusID', 'AfgKode'):=NULL] 
setkey(farminfo, 'markpolyID')
write.csv(farminfo, file = 'o:/ST_LandskabsGenerering/outputs/FarmInfo2013CleanOct2015.csv',
 row.names = FALSE)