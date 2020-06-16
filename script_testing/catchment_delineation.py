import sys
sys.path.append('../code/')

from Functions import *

# Input
workspace = arcpy.GetParameterAsText(0)
input_raster = arcpy.GetParameterAsText(1)
catchment_area = arcpy.GetParameterAsText(2)
output_catchments = arcpy.GetParameterAsText(3)

catchment_delineation(workspace, input_raster, catchment_area, output_catchments)
arcpy.AddMessage('Success!')
