from functions import *

# Input data
workspace = arcpy.GetParameterAsText(0)  # Output and scratch workspace
fastighetskartan_markytor = arcpy.GetParameterAsText(1)  # Land use

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.nodata = "NONE"

fastighetskartan_markytor_simplifed(workspace, fastighetskartan_markytor)
