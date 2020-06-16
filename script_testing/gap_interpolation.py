import sys
sys.path.append('../code/')

from Functions import *

workspace = arcpy.GetParameterAsText(0)
radius = arcpy.GetParameterAsText(1)
input_raster = arcpy.GetParameterAsText(2)
output_raster = arcpy.GetParameterAsText(3)

out = gap_interpolation(radius, input_raster)
output_raster = workspace + r"/" + output_raster
out.save(output_raster)
arcpy.AddMessage('Success!')
