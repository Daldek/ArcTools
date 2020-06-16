import sys
sys.path.append('../code/')

from Functions import *

# Input
workspace = arcpy.GetParameterAsText(0)
input_raster = arcpy.GetParameterAsText(1)
cell_size = arcpy.GetParameterAsText(2)
water_bodies = arcpy.GetParameterAsText(3)

raster_endorheic_modification(workspace, input_raster, cell_size, water_bodies)
arcpy.AddMessage('Success!')
