import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

# input data
workspace = arcpy.GetParameterAsText(0)
dem = arcpy.GetParameterAsText(1)
chosen_catchments = arcpy.GetParameterAsText(2)
cell_size = arcpy.GetParameterAsText(3)  # temporary! Will be removed later

# output file
model_area = arcpy.GetParameterAsText(4)

# Local variables
catchment = workspace + r"/catchment"
catchment_buffer = workspace + r"/catchment_buffer"
rasterized_buffer = workspace + r"/rasterized_buffer"
clipped_dem = workspace + r"/clipped_dem"

field_name = "elevaton"

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem
arcpy.env.nodata = "NONE"

# DEM extent
left = arcpy.GetRasterProperties_management(dem, "LEFT")
bottom = arcpy.GetRasterProperties_management(dem, "BOTTOM")
right = arcpy.GetRasterProperties_management(dem, "RIGHT")
top = arcpy.GetRasterProperties_management(dem, "TOP")
extent = str(left) + " " + str(bottom) + " " + str(right) + " " + str(top)

# Add field
arcpy.AddField_management(chosen_catchments, field_name, "SHORT")
arcpy.AddMessage("New field has been created.")

# Calculate field
arcpy.CalculateField_management(chosen_catchments, field_name, 999, "PYTHON_9.3")
arcpy.AddMessage("Values have been assigned.")

# Dissolve
arcpy.Dissolve_management(chosen_catchments, catchment, field_name, "", "MULTI_PART")
arcpy.AddMessage('New cathchment has been created.')

# Clip
arcpy.Clip_management(dem, extent, clipped_dem, catchment, "999", "ClippingGeometry", "NO_MAINTAIN_EXTENT")

# Buffer
buffer_dist = int(cell_size) * 2
arcpy.Buffer_analysis(catchment, catchment_buffer, buffer_dist, 'OUTSIDE_ONLY')
arcpy.AddMessage("Buffer has been created.")

# Rasterize
arcpy.FeatureToRaster_conversion(catchment_buffer, field_name, rasterized_buffer, cell_size)
arcpy.AddMessage("Raster has been built. Build? Eh...")

# Mosaic to new raster
arcpy.MosaicToNewRaster_management("rasterized_buffer; clipped_dem", workspace, "ModelArea", "", "16_BIT_UNSIGNED",
                                   cell_size, 1, "FIRST", "FIRST")
