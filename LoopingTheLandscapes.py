# Looping through the landscapes
# Snippet to set up directory structure and copy files into it
# Date Sep 29 2015
# Author: Lars Dalby

import shutil, os

# Names of the new landscapes
NJ = ['NJ1', 'NJ2', 'NJ3', 'NJ4', 'NJ5', 'NJ6']
VJ = ['NJ1', 'NJ2', 'NJ3', 'NJ4', 'NJ5']
OJ = ['OJ1', 'OJ2', 'OJ3', 'OJ4']
FU = ['FU1', 'FU2', 'FU3', 'FU4']
NS = ['NS1', 'NS2', 'NS3', 'NS4']
SS = ['SS1', 'SS2', 'SS3', 'SS4', 'SS5', 'SS6']
BO = 'BO'
landscapes = NJ + VJ + OJ + FU + NS + SS + BO

# Path to the template directory:
template = "c:/Users/lada/Desktop/Skabelon/"

# Path to the destination
dst = "c:/Users/lada/Desktop/NewSet/"

# Copy the template directory
for index in range(len(landscapes)):
   shutil.copytree(template, os.path.join(dst,landscapes[index]))
                    
