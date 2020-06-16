import sys
sys.path.append('../code/')

from Functions import *

# Input
workspace = arcpy.GetParameterAsText(0)
river_network = arcpy.GetParameterAsText(1)
endorheic_water_bodies = arcpy.GetParameterAsText(2)
input_raster = arcpy.GetParameterAsText(3)
maximum_distance = int(arcpy.GetParameterAsText(4))
smooth_drop = int(arcpy.GetParameterAsText(5))
sharp_drop = int(arcpy.GetParameterAsText(6))

raster_manipulation(workspace, input_raster, river_network, maximum_distance,
                    smooth_drop, sharp_drop, endorheic_water_bodies)
arcpy.AddMessage('Success!')
