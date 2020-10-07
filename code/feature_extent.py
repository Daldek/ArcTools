import arcpy
from Functions import feature_extent

# Input
feature = arcpy.GetParameterAsText(0)

extent = feature_extent(feature)
arcpy.AddMessage('Feature extent ' + str(extent))
arcpy.AddMessage('Success!')
