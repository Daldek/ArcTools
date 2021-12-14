import os
import shutil
from functions import *
from classes import *

arcpy.AddMessage('Off we go!')

# Where am I?
current_dir_path = os.getcwd()
current_dir_name = os.path.basename(current_dir_path)
if current_dir_name == "ArcTools":
    os.chdir(current_dir_path + r"\code")

# I have no idea what the code test should look like <lenny face>
try:
    shutil.rmtree(r"..\temp\test_output")
except:
    pass
os.mkdir(r"..\temp\test_output")
current_user = os.getenv('username')
workspace = "C:\\Users\\" + current_user + "\\Documents\\ArcGIS\\Default.gdb"
print("Current user: " + current_user + "\nWorkspace: " + workspace)

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
rise = 5
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

# 3 - catchment processing (without additional rasters)
catchment_delineation(workspace, agree_dem, catchment_area)
# catchments = workspace + r"\catchments"  # I do not want to use all catchments anymore
arcpy.AddMessage("Step 3 - complete!\n")

# 4 - catchment processing (with additional rasters)
catchment_delineation(workspace, agree_dem, catchment_area, True, True, True)
# catchments = workspace + r"\catchments"  # I do not want to use all catchments anymore
arcpy.AddMessage("Step 4 - complete!\n")

# 5 - domain creation (with catchment simplification)
domain_creation(workspace, in_dem, rise, in_selected_catchment,
                in_buildings, buffer_distance, output_folder, True)
arcpy.AddMessage("Step 5 - complete!\n")

# 6 - domain creation (without catchment simplification)
domain_creation(workspace, in_dem, rise, in_selected_catchment,
                in_buildings, buffer_distance, output_folder, False)
arcpy.AddMessage("Step 6 - complete!\n")

buffer_distance = 0
# 7 - domain creation (with catchment simplification, but without buffer)
domain_creation(workspace, in_dem, rise, in_selected_catchment,
                in_buildings, buffer_distance, output_folder, True)
arcpy.AddMessage("Step 7 - complete!\n")

# 8 - export to ascii and validation
mask = r"..\temp\test_output\bathymetry.asc"
in_rasters = [r'..\data.gdb\in_landuse_sweref1800', r'..\data.gdb\in_raster_sweref1800']
mask_and_export(mask, in_rasters, output_folder)
arcpy.AddMessage("Step 8 - complete!\n")

# clean up
arcpy.AddMessage('One moment, please...')
arcpy.Delete_management("in_memory")
os.remove('log')
os.remove('.prj')
arcpy.AddMessage('Ready!')
