from code.Functions import *
arcpy.CheckOutExtension("Spatial")

# input data
workspace = arcpy.GetParameterAsText(0)
input_raster = arcpy.GetParameterAsText(1)
catchment_area = arcpy.GetParameterAsText(2)
if catchment_area == "#":
    catchment_area = 0.25  # unit - square kilometers

# output file
output_catchments = arcpy.GetParameterAsText(3)

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = input_raster
arcpy.env.cellSize = input_raster
arcpy.env.nodata = "NONE"

catchment_delineation(workspace, input_raster, catchment_area, output_catchments)
