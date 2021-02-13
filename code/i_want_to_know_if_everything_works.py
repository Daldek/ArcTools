import os
import shutil
from functions import *
from classes import *

# I have no idea what the code test should look like <lenny face>
os.mkdir(r"..\temp\test_output")
workspace = r"C:\Users\PLPD00293\Documents\ArcGIS\Default.gdb"

# main scripts
# input data
in_dem = r"..\data.gdb\in_raster_sweref1800"
in_landuse = r"..\data.gdb\in_landuse_sweref1800"
in_culverts = r"..\data.gdb\In_culverts_sweref1800"
in_buildings = r"..\data.gdb\In_buildings_sweref1800"
in_lake = r""
in_selected_catchment = r"..\data.gdb\in_selected_catchment"

# variables
maximum_distance = 4
smooth_drop = 2
catchment_area = 0.05
sharp_drop = 10
inclination = 30
buffer_distance = 10
output_folder = r"..\temp\test_output"

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = in_dem
arcpy.env.cellSize = in_dem
arcpy.env.nodata = "NONE"

# 1 - raster manipulation (without AgreeDEM)
raster_manipulation(workspace, in_dem, in_culverts, maximum_distance, smooth_drop, sharp_drop, in_lake, False)
arcpy.AddMessage("Step 1 - complete!\n")

# 2 - raster manipulation (with AgreeDEM)
raster_manipulation(workspace, in_dem, in_culverts, maximum_distance, smooth_drop, sharp_drop, in_lake, True)
agree_dem = workspace + r"\AgreeDEM"
filled_channels = workspace + r"\Filled_channels"
arcpy.AddMessage("Step 2 - complete!\n")

# 3 - catchment processing
catchment_delineation(workspace, agree_dem, catchment_area)
# catchments = workspace + r"\catchments"  # I do not want to use all catchments anymore
arcpy.AddMessage("Step 3 - complete!\n")

# 4 - domain creation
domain_creation(workspace, in_dem, 5, in_selected_catchment,
                in_buildings, in_landuse, inclination, buffer_distance, output_folder)
arcpy.AddMessage("Step 4 - complete!\n")
arcpy.AddMessage('Success!')

# 5 - validation
land_use = AscFile(r"..\temp\test_output\land_use.asc")
model_domain = AscFile(r"..\temp\test_output\model_domain.asc")
roughness = AscFile(r"..\temp\test_output\roughness.asc")

if land_use.get_properties() == model_domain.get_properties() == roughness.get_properties():
    print("Hurrey!")

# clean up
shutil.rmtree(r"..\temp\test_output")
