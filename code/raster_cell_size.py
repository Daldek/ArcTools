import arcpy
from functions import raster_cell_size

# Input
input_raster = arcpy.GetParameterAsText(0)

cell_size = raster_cell_size(input_raster)
arcpy.AddMessage('Raster cell size ' + str(cell_size))
arcpy.AddMessage('Success!')
