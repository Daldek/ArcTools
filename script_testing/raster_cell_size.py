import sys
sys.path.append('../code/')

from Functions import *

# Input
input_raster = arcpy.GetParameterAsText(0)

cell_size = raster_cell_size(input_raster)
arcpy.AddMessage('Raster cell size ' + str(cell_size))
arcpy.AddMessage('Success!')
