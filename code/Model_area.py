import arcpy
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")

# input data
workspace = arcpy.GetParameterAsText(0)  # Geodatabase
elevation_model = arcpy.GetParameterAsText(1)  # Raster
chosen_catchments = arcpy.GetParameterAsText(2)  # Polygons
buildings = arcpy.GetParameterAsText(3)  # Polygons
landuse = arcpy.GetParameterAsText(4)  # Raster

# output
output_folder = arcpy.GetParameterAsText(5)  # Not a geodatabase

# Local variables
field_name = "elevaton"
inclination = 30

# DEM
catchment = workspace + r"/catchment"
catchment_buffer = workspace + r"/catchment_buffer"
rasterized_buffer = workspace + r"/rasterized_buffer"
buildings_elev = workspace + r"/buildings_elev"
rasterized_buildings = workspace + r"/rasterized_buildings"
rasterized_buildings_calc = workspace + r"/rasterized_buildings_calc"
clipped_dem = workspace + r"/clipped_dem"
dem_buildings = workspace + r"/dem_buildings"

# Land use grid
land_use_clip = workspace + r"/land_use_clip"

# Roughness grid
slope_grid = workspace + r"/slope_grid"
steep_slopes_grid = workspace + r"/steep_slopes_grid"
steep_slopes_grid_clip = workspace + r"/steep_slopes_grid_clip"

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = elevation_model
arcpy.env.cellSize = elevation_model
arcpy.env.nodata = "NONE"

# DEM extent
left = arcpy.GetRasterProperties_management(elevation_model, "LEFT")
bottom = arcpy.GetRasterProperties_management(elevation_model, "BOTTOM")
right = arcpy.GetRasterProperties_management(elevation_model, "RIGHT")
top = arcpy.GetRasterProperties_management(elevation_model, "TOP")
extent = str(left) + " " + str(bottom) + " " + str(right) + " " + str(top)  # does not look nice

# DEM cell size
cell_size_x_direction = arcpy.GetRasterProperties_management(elevation_model, "CELLSIZEX")
cell_size_y_direction = arcpy.GetRasterProperties_management(elevation_model, "CELLSIZEY")
cell_size_x_direction = float(cell_size_x_direction.getOutput(0))
cell_size_y_direction = float(cell_size_y_direction.getOutput(0))
cell_size = (cell_size_x_direction + cell_size_y_direction) / 2
if cell_size_x_direction != cell_size_y_direction:
    arcpy.AddMessage("Cell size in the x-direction is different from cell size in the y-direction!")


'''
NEW DIGITAL ELEVATION MODEL
'''
# Catchment
# Add field
arcpy.AddField_management(chosen_catchments, field_name, "SHORT")
arcpy.AddMessage("New field has been created.")

# Calculate field
arcpy.CalculateField_management(chosen_catchments, field_name, 999, "PYTHON_9.3")
arcpy.AddMessage("Values have been assigned.")

# Dissolve
arcpy.Dissolve_management(chosen_catchments, catchment, field_name, "", "MULTI_PART")
arcpy.AddMessage("New catchment has been created.")

# Buildings
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
calc = Raster(elevation_model) + Raster(rasterized_buildings)
calc.save(rasterized_buildings_calc)
arcpy.AddMessage("New elevations have been calculated.")

# Mosaic to new raster
dem_buildings_input = str("rasterized_buildings_calc; ") + str(elevation_model)
arcpy.MosaicToNewRaster_management(dem_buildings_input, workspace, "dem_buildings", "#",
                                   "32_BIT_FLOAT", cell_size, 1, "FIRST", "FIRST")
arcpy.AddMessage("New DEM has been built.")

# Model area
# Clip
arcpy.Clip_management(dem_buildings, extent, clipped_dem, catchment, "999", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
arcpy.AddMessage("DEM has been clipped.")

# Buffer
buffer_dist = int(cell_size) * 2
arcpy.Buffer_analysis(catchment, catchment_buffer, buffer_dist, "OUTSIDE_ONLY")
arcpy.AddMessage("Buffer has been created.")

# Rasterize
arcpy.FeatureToRaster_conversion(catchment_buffer, field_name, rasterized_buffer, cell_size)
arcpy.AddMessage("Buffer has been rasterized.")

# Mosaic to new raster
arcpy.MosaicToNewRaster_management("clipped_dem; rasterized_buffer", workspace, "model_domain_grid", "#",
                                   "32_BIT_FLOAT", cell_size, 1, "FIRST", "FIRST")
arcpy.AddMessage("Domain raster has been built.")

# model_domain_grid = workspace + r"/model_domain_grid"

'''
LAND USE GRID
'''
# Clip
arcpy.Clip_management(landuse, extent, land_use_clip, catchment, "#", "ClippingGeometry",
                      "NO_MAINTAIN_EXTENT")
arcpy.AddMessage("Land use raster has been clipped.")

# Mosaic to new raster
arcpy.MosaicToNewRaster_management("land_use_clip; rasterized_buffer", workspace, "landuse_grid", "#",
                                   "16_BIT_UNSIGNED", cell_size, 1, "FIRST", "FIRST")
arcpy.AddMessage("Lands use raster has been built.")

'''
ROUGHNESS GRID (LAND USE + STEEP SLOPES)
'''
# Slope
arcpy.Slope_3d(dem_buildings, slope_grid, "DEGREE", 1.0)
arcpy.AddMessage("Slopes have been calculated.")

# Reclassify
additional_roughness = Reclassify(slope_grid, "Value", RemapRange([[0, inclination, "NODATA"],
                                                                   [inclination, 180, 998]]))
additional_roughness.save(steep_slopes_grid)
arcpy.AddMessage("Raster has been reclassified.")

# Clip
arcpy.Clip_management(steep_slopes_grid, extent, steep_slopes_grid_clip, catchment, "#", "ClippingGeometry",
                      "NO_MAINTAIN_EXTENT")
arcpy.AddMessage("Land use raster has been clipped.")

# Mosaic to new raster
arcpy.MosaicToNewRaster_management("steep_slopes_grid_clip; landuse_grid", workspace, "roughness_grid", "",
                                   "16_BIT_UNSIGNED", cell_size, 1, "FIRST", "FIRST")
arcpy.AddMessage("Roughness raster has been built.")

'''
DATA EXPORT
'''
# Model domain to ASCII
output_file = output_folder + str("/model_domain.asc")
arcpy.RasterToASCII_conversion("model_domain_grid", output_file)
arcpy.AddMessage("Model domain raster has been exported to ASCII.")

# Land use to ASCII
output_file = output_folder + str("/land_use.asc")
arcpy.RasterToASCII_conversion("landuse_grid", output_file)
arcpy.AddMessage("Land use raster has been exported to ASCII.")

# Land use to ASCII
output_file = output_folder + str("/roughness.asc")
arcpy.RasterToASCII_conversion("roughness_grid", output_file)
arcpy.AddMessage("Roughness raster has been exported to ASCII.")

# Delete temp files
arcpy.Delete_management(rasterized_buildings)
arcpy.Delete_management(rasterized_buildings_calc)
arcpy.Delete_management(dem_buildings)
arcpy.Delete_management(clipped_dem)
arcpy.Delete_management(catchment_buffer)
arcpy.Delete_management(rasterized_buffer)
arcpy.Delete_management(land_use_clip)
arcpy.Delete_management(slope_grid)
arcpy.Delete_management(steep_slopes_grid)
arcpy.Delete_management(steep_slopes_grid_clip)
