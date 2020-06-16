# import sys
# sys.path.append('../')
#
# from code.Functions import *
import sys
sys.path.append('../code/')

from Functions import *

workspace = arcpy.GetParameterAsText(0)
input_raster = arcpy.GetParameterAsText(1)
rise = int(arcpy.GetParameterAsText(2))
catchments = arcpy.GetParameterAsText(3)
buildings = arcpy.GetParameterAsText(4)
landuse_raster = arcpy.GetParameterAsText(5)
output_raster = arcpy.GetParameterAsText(6)

domain_creation(workspace, input_raster, rise, catchments, buildings, landuse_raster, output_raster)
arcpy.AddMessage('Success!')
