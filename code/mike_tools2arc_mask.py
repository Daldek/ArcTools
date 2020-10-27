from Functions import *

# Input data
workspace = arcpy.GetParameterAsText(0)
cell_size = arcpy.GetParameterAsText(1)
input_depth_raster = arcpy.GetParameterAsText(2)
threshold_value = arcpy.GetParameterAsText(3)
nodata_polygons = arcpy.GetParameterAsText(4)
domain = arcpy.GetParameterAsText(5)

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
# arcpy.env.snapRaster = dem
arcpy.env.cellSize = cell_size
arcpy.env.nodata = "NONE"

out_raster_path = workspace + r"/out_Mike2Arc"

out_raster = mike_tools2arc_mask(workspace, cell_size, input_depth_raster, threshold_value, nodata_polygons, domain)
out_raster.save(out_raster_path)
arcpy.RefreshCatalog(workspace)
