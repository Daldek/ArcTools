from functions import *

# Input data
workspace = arcpy.GetParameterAsText(0)
cell_size = arcpy.GetParameterAsText(1)
input_raster = arcpy.GetParameterAsText(2)
threshold_value = arcpy.GetParameterAsText(3)
nodata_polygons = arcpy.GetParameterAsText(4)
domain = arcpy.GetParameterAsText(5)

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = input_raster
arcpy.env.cellSize = cell_size
arcpy.env.nodata = "NONE"

out_raster_path = input_raster + r"_mask"

out_raster = mask_below_threshold(workspace, cell_size, input_raster, threshold_value, nodata_polygons, domain)
out_raster.save(out_raster_path)
arcpy.RefreshCatalog(workspace)
