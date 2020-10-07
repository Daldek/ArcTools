from Functions import *

# input data
workspace = arcpy.GetParameterAsText(0)  # Output and scratch workspace
input_raster = arcpy.GetParameterAsText(1)  # Hydrologically correct raster. "AgreeDEM" from "DEM_manipulation.py"
catchment_area = arcpy.GetParameterAsText(2)  # Desired area of single catchment
if catchment_area == "#":
    catchment_area = 0.25  # unit - square kilometers

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = input_raster
arcpy.env.cellSize = input_raster
arcpy.env.nodata = "NONE"

catchment_delineation(workspace, input_raster, catchment_area)
