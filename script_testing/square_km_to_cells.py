import sys
sys.path.append('../code/')

from Functions import *

# Input
input_raster = arcpy.GetParameterAsText(0)
area = arcpy.GetParameterAsText(1)

cell_size = raster_cell_size(input_raster)
arcpy.AddMessage('Raster cell size ' + str(cell_size))

number_of_cells = square_km_to_cells(area, cell_size)
arcpy.AddMessage('Number of cells ' + str(number_of_cells))
arcpy.AddMessage('Success!')
