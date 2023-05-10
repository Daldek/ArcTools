from functions import *

# input data
workspace = arcpy.GetParameterAsText(0)  # Output and scratch workspace
input_dem = arcpy.GetParameterAsText(1)  # Hydrologically correct raster. "AgreeDEM" from "dem_manipulation.py"
input_correct_dem = arcpy.GetParameterAsText(2)  # "AgreeDEM" from function "raster_manipulation" or any other depressionless raster
catchment_area = arcpy.GetParameterAsText(3)  # Desired area of single catchment
if catchment_area == "#":
    catchment_area = 0.25  # unit - square kilometers

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = input_dem
arcpy.env.cellSize = input_dem
arcpy.env.nodata = "NONE"

catchment_delineation(workspace, input_dem, input_correct_dem, catchment_area)
