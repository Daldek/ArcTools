import sys
sys.path.append('../code/')

from Functions import *

# Input
feature = arcpy.GetParameterAsText(0)

extent = feature_extent(feature)
arcpy.AddMessage('Feature extent ' + str(extent))
arcpy.AddMessage('Success!')
