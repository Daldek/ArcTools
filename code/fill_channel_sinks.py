from functions import *

workspace = arcpy.GetParameterAsText(0)
input_raster = arcpy.GetParameterAsText(1)
channel_width = arcpy.GetParameterAsText(2)
channel_axis = arcpy.GetParameterAsText(3)

fill_channel_sinks(workspace, input_raster, channel_width, channel_axis)
arcpy.AddMessage('Success!')
