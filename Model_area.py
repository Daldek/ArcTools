import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

# input data
workspace = arcpy.GetParameterAsText(0)  # Geodatabase
dem = arcpy.GetParameterAsText(1)  # Raster
chosen_catchments = arcpy.GetParameterAsText(2)  # Polygons
buildings = arcpy.GetParameterAsText(3)  # Polygons
landuse = arcpy.GetParameterAsText(4)  # Raster

# output
output_folder = arcpy.GetParameterAsText(5)  # Not a geodatabase

# Local variables
buildings_elev = workspace + r"/buildings_elev"
rasterized_buildings_clip = workspace + r"/rasterized_buildings_clip"
rasterized_buildings = workspace + r"/rasterized_buildings"
rasterized_buildings_calc = workspace + r"/rasterized_buildings_calc"
dem_buildings = workspace + r"/dem_buildings"
landuse_clip = workspace + r"/landuse_clip"
roughness_grid = workspace + r"/roughness_grid"
catchment = workspace + r"/catchment"
catchment_buffer = workspace + r"/catchment_buffer"
rasterized_buffer = workspace + r"/rasterized_buffer"
clipped_dem = workspace + r"/clipped_dem"
slope_grid = workspace + r"/slope_grid"
slope_roughness = workspace + r"/slope_roughness"

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
arcpy.AddMessage("New catchment has been created.")

# Add field
arcpy.AddField_management(buildings, field_name, "SHORT")
arcpy.AddMessage("New field has been created.")

# Calculate field
arcpy.CalculateField_management(buildings, field_name, 5, "PYTHON_9.3")
arcpy.AddMessage("Values have been assigned.")

# Feature to raster
arcpy.FeatureToRaster_conversion(buildings, field_name, rasterized_buildings, cell_size)
arcpy.AddMessage("Buildings have been rasterized.")

# Raster calculator
calc = Raster(dem) + Raster(rasterized_buildings)
calc.save(rasterized_buildings_calc)
arcpy.AddMessage("New building elevations have been calculated.")

# Clip
arcpy.Clip_management(rasterized_buildings_calc, extent, rasterized_buildings_clip, catchment, "#", "ClippingGeometry",
                      "NO_MAINTAIN_EXTENT")
arcpy.AddMessage("Buildings have been clipped.")

# Mosaic to new raster
arcpy.MosaicToNewRaster_management("rasterized_buildings_clip; clipped_dem", workspace, "dem_buildings", "",
                                   "32_BIT_FLOAT", cell_size, 1, "FIRST", "FIRST")
arcpy.AddMessage("New DEM has been built.")

# Slope
arcpy.Slope_3d(dem_buildings, slope_grid, "DEGREE", 1.0)
arcpy.AddMessage("Slopes have been calculated.")

# Reclassify
additional_roughness = Reclassify(slope_grid, "Value", RemapRange([[0, 30, "NODATA"], [30, 180, 998]]))
additional_roughness.save(slope_roughness)
arcpy.AddMessage("Raster has been reclassified.")

# Clip
arcpy.Clip_management(landuse, extent, landuse_clip, catchment, "#", "ClippingGeometry",
                      "NO_MAINTAIN_EXTENT")
arcpy.AddMessage("Land use raster has been clipped.")

# Mosaic to new raster
arcpy.MosaicToNewRaster_management("slope_roughness; landuse_clip", workspace, "roughness_grid", "",
                                   "32_BIT_FLOAT", cell_size, 1, "FIRST", "FIRST")
arcpy.AddMessage("Roughness raster has been built.")

# Clip
arcpy.Clip_management(dem, extent, clipped_dem, catchment, "999", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
arcpy.AddMessage("DEM has been clipped.")

# Buffer
buffer_dist = int(cell_size) * 2
arcpy.Buffer_analysis(catchment, catchment_buffer, buffer_dist, "OUTSIDE_ONLY")
arcpy.AddMessage("Buffer has been created.")

# Rasterize
arcpy.FeatureToRaster_conversion(catchment_buffer, field_name, rasterized_buffer, cell_size)
arcpy.AddMessage("Buffer has been rasterized.")

# Mosaic to new raster
arcpy.MosaicToNewRaster_management("rasterized_buffer; dem_buildings", workspace, "ModelArea", "", "32_BIT_FLOAT",
                                   cell_size, 1, "FIRST", "FIRST")
arcpy.AddMessage("Raster has been built.")

ModelArea = workspace + r"/ModelArea"

# # Raster to ASCII
# arcpy.RasterToASCII_conversion(ModelArea, model_area)
# arcpy.AddMessage("Raster has been exported to ASCII.")

# Delete temp files
arcpy.Delete_management(rasterized_buildings)
arcpy.Delete_management(rasterized_buildings_calc)
arcpy.Delete_management(rasterized_buildings_clip)
arcpy.Delete_management(slope_grid)
arcpy.Delete_management(slope_roughness)
arcpy.Delete_management(clipped_dem)
arcpy.Delete_management(catchment_buffer)
