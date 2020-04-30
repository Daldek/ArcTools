import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

# input data
workspace = arcpy.GetParameterAsText(0)
dem = arcpy.GetParameterAsText(1)
chosen_catchments = arcpy.GetParameterAsText(2)

# output file
model_area = arcpy.GetParameterAsText(3)

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
extent = str(left) + " " + str(bottom) + " " + str(right) + " " + str(top)  # does not look nice

# DEM cell size
cell_size_x_direction = arcpy.GetRasterProperties_management(dem, "CELLSIZEX")
cell_size_y_direction = arcpy.GetRasterProperties_management(dem, "CELLSIZEY")
cell_size_x_direction = float(cell_size_x_direction.getOutput(0))
cell_size_y_direction = float(cell_size_y_direction.getOutput(0))
cell_size = (cell_size_x_direction + cell_size_y_direction) / 2
if cell_size_x_direction != cell_size_y_direction:
    arcpy.AddMessage("Cell size in the x-direction is different from cell size in the y-direction!")

# Add field
arcpy.AddField_management(chosen_catchments, field_name, "SHORT")
arcpy.AddMessage("New field has been created.")

# Calculate field
arcpy.CalculateField_management(chosen_catchments, field_name, 999, "PYTHON_9.3")
arcpy.AddMessage("Values have been assigned.")

# Dissolve
arcpy.Dissolve_management(chosen_catchments, catchment, field_name, "", "MULTI_PART")
arcpy.AddMessage("New cathchment has been created.")

# Clip
arcpy.Clip_management(dem, extent, clipped_dem, catchment, "999", "ClippingGeometry", "NO_MAINTAIN_EXTENT")

# Buffer
buffer_dist = int(cell_size) * 2
arcpy.Buffer_analysis(catchment, catchment_buffer, buffer_dist, "OUTSIDE_ONLY")
arcpy.AddMessage("Buffer has been created.")

# Rasterize
arcpy.FeatureToRaster_conversion(catchment_buffer, field_name, rasterized_buffer, cell_size)
arcpy.AddMessage("Buffer has been rasterized.")

# Mosaic to new raster
arcpy.MosaicToNewRaster_management("rasterized_buffer; clipped_dem", workspace, "ModelArea", "", "32_BIT_FLOAT",
                                   cell_size, 1, "FIRST", "FIRST")
arcpy.AddMessage("Raster has been built.")

ModelArea = workspace + r"/ModelArea"

# Raster to ASCII
arcpy.RasterToASCII_conversion(ModelArea, model_area)
arcpy.AddMessage("Raster has been exported to ASCII.")
