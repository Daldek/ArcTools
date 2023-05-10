# -*- coding: utf-8 -*-

import os
import shutil
from functions import *
from classes import *

arcpy.AddMessage('Off we go!')

# Where am I?
current_dir_path = os.getcwd()
arcpy.AddMessage("cwd path: " + str(current_dir_path))
current_dir_name = os.path.basename(current_dir_path)
if current_dir_name == "ArcTools":
    os.chdir(current_dir_path + r"/code")

# I have no idea what the code test should look like <lenny face>
try:
    shutil.rmtree(r"../temp/test_output")
except:
    pass
os.mkdir(r"../temp/test_output")
current_user = os.getenv('username')
workspace = "C:/Users/" + current_user + "/Documents/ArcGIS/Default.gdb"
print("Current user: " + current_user + "\nWorkspace: " + workspace)

# main scripts
# input data
in_dem = r"../data.gdb/in_raster_sweref1800"
in_landuse = r"../data.gdb/in_landuse_sweref1800"
in_culverts = r"../data.gdb/in_culverts_sweref1800"
in_buildings = r"../data.gdb/in_buildings_sweref1800"
in_lake = r""
in_selected_catchment = r"../data.gdb/in_selected_catchment"
in_fastighetskartan_markytor = r"../data.gdb/in_fastighetskartan_markytor_sweref99tm"
in_buildings2 = r"../data.gdb/in_buildings_sweref99tm"
in_depth_sweref99tm = r"../data.gdb/in_depth_sweref99tm"


# variables
maximum_distance = 4
smooth_drop = 2
catchment_area = 0.05
sharp_drop = 10
rise = 5
buffer_distance = 10
output_folder = current_dir_path + r"/temp/test_output"
arcpy.AddMessage("Output folder for shp: " + str(output_folder))

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
agree_dem = workspace + r"/script_agreeDEM"
filled_channels = workspace + r"/script_filled_channels"
arcpy.AddMessage("Step 2 - complete!\n")

# 3 - catchment processing (without additional rasters)
catchment_delineation(workspace, in_dem, agree_dem, catchment_area)
catchments = workspace + r"/catchments"  # I do not want to use all catchments anymore
arcpy.AddMessage("Step 3 - complete!\n")

# 4 - Generating longest flowpath for a catchment
flow_dir_raster = workspace + r"/script_flow_dir"
longest_flow_path(workspace, flow_dir_raster, '')
arcpy.AddMessage("Step 4 - complete!\n")

# 5 - Generating longest flowpath for a catchment (additional input data)
flow_dir_raster = workspace + r"/script_flow_dir"
flow_ln_raster = workspace + r"/script_flow_ln"
longest_flow_path(workspace, flow_dir_raster, flow_ln_raster)
arcpy.AddMessage("Step 5 - complete!\n")

# 6 - domain creation (with catchment simplification)
domain_creation(workspace, in_dem, rise, in_selected_catchment,
                in_buildings, buffer_distance, output_folder, True)
arcpy.AddMessage("Step 6 - complete!\n")

# 7 - domain creation (without catchment simplification)
domain_creation(workspace, in_dem, rise, in_selected_catchment,
                in_buildings, buffer_distance, output_folder, False)
arcpy.AddMessage("Step 7 - complete!\n")

buffer_distance = 0
# 8 - domain creation (with catchment simplification, but without buffer)
domain_creation(workspace, in_dem, rise, in_selected_catchment,
                in_buildings, buffer_distance, output_folder, True)
arcpy.AddMessage("Step 8 - complete!\n")

# 9 - export to ascii and validation
mask = r"../temp/test_output/bathymetry.asc"
in_rasters = [r'../data.gdb/in_landuse_sweref1800', r'../data.gdb/in_raster_sweref1800']
mask_and_export(mask, in_rasters, output_folder)
arcpy.AddMessage("Step 9 - complete!\n")

# 10 - Fastighetskartan. Simplify and export
fastighetskartan_markytor_simplifed(workspace, in_fastighetskartan_markytor)
arcpy.AddMessage("Step 10 - complete!\n")

# 11 - infrastructure at risk
infrastructure_at_risk(workspace, [10, 100.0], in_buildings2, in_depth_sweref99tm)
arcpy.AddMessage("Step 11 - complete!\n")

# clean up
arcpy.AddMessage('One moment, please...')
arcpy.Delete_management("in_memory")
try:
    os.remove('log')
except:
    pass
try:
    os.remove('.prj')
except:
    pass
arcpy.AddMessage('Ready!')
