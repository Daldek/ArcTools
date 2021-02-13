from functions import *

# Input data
workspace = arcpy.GetParameterAsText(0)  # geodatabase
cell_size = arcpy.GetParameterAsText(1)  # meters, optional
input_raster = arcpy.GetParameterAsText(2)  # must be saved in a geodatabase
threshold_value = arcpy.GetParameterAsText(3)  # lower values will be removed
nodata_polygons = arcpy.GetParameterAsText(4)  # where to set null values, optional
domain = arcpy.GetParameterAsText(5)  # feature class, polygon, optional

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = input_raster
arcpy.env.nodata = "NONE"
if cell_size != '':
    arcpy.env.cellSize = input_raster
else:
    arcpy.env.cellSize = cell_size

out_raster_path = input_raster + r"_mask"

out_raster = mask_below_threshold(workspace, cell_size, input_raster, threshold_value, nodata_polygons, domain)
out_raster.save(out_raster_path)

# Extract by mask
masked_raster = ExtractByMask(input_raster, out_raster)

arcpy.RefreshCatalog(workspace)
