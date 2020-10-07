from Functions import *

# Input data
workspace = arcpy.GetParameterAsText(0)  # Output and scratch workspace
input_raster = arcpy.GetParameterAsText(1)  # "filled_channels" raster from "DEM_manipulation.py"
rise = int(arcpy.GetParameterAsText(2))  # building heights
catchments = arcpy.GetParameterAsText(3)  # selected catchments. From "Catchment_processing.py"
buildings = arcpy.GetParameterAsText(4)  # Polygon feature class
landuse_raster = arcpy.GetParameterAsText(5)  # Raster
inclination = arcpy.GetParameterAsText(6)
# Unit: degree. For slopes greather then specified inclination, new land use class will be created
output_folder = arcpy.GetParameterAsText(7)  # Where the ASCII files will be saved

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = input_raster
arcpy.env.cellSize = input_raster
arcpy.env.nodata = "NONE"

domain_creation(workspace, input_raster, rise, catchments,
                buildings, landuse_raster, inclination, output_folder)
arcpy.AddMessage('Success!')
