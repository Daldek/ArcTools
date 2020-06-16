import sys
sys.path.append('../code/')

from Functions import *

# Input
input_raster = arcpy.GetParameterAsText(0)

extent = raster_extent(input_raster)
arcpy.AddMessage('Raster extent ' + str(extent))
arcpy.AddMessage('Success!')
