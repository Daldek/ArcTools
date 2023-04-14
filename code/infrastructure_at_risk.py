import os
from functions import *

workspace = arcpy.GetParameterAsText(0)  # Output and scratch workspace
depths = arcpy.GetParameterAsText(1)  # List of water depths to be analysed
input_infrastructure = arcpy.GetParameterAsText(2)  # Such as buildings, roads, etc
input_water_depth_raster = arcpy.GetParameterAsText(3)

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True

depths = list(depths.replace(',', '').split(' '))  # remove separators and convert to lsit
depths = [float(i) for i in depths]  # convert string to float

infrastructure_at_risk(workspace, 
                       depths, 
                       input_infrastructure, 
                       input_water_depth_raster)
arcpy.AddMessage('Success!')
