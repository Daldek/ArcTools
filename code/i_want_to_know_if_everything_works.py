from functions import *

# I have no idea what the code test should look like

workspace = r"C:\Users\PLPD00293\Documents\ArcGIS\Default.gdb"

# main scripts
# input data
in_dem = r"C:\Users\PLPD00293\Documents\!Python\ArcTools\data.gdb\in_raster_sweref1800"
in_landuse = r"C:\Users\PLPD00293\Documents\!Python\ArcTools\data.gdb\in_landuse_sweref1800"
in_culverts = r"C:\Users\PLPD00293\Documents\!Python\ArcTools\data.gdb\In_culverts_sweref1800"
in_buildings = r"C:\Users\PLPD00293\Documents\!Python\ArcTools\data.gdb\In_buildings_sweref1800"
in_lake = r""

# variables
maximum_distance = 4
smooth_drop = 2
catchment_area = 0.05
sharp_drop = 10
inclination = 30
output_folder = r"C:\Users\PLPD00293\Documents\!Python\ArcTools\temp\test_output"

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = in_dem
arcpy.env.cellSize = in_dem
arcpy.env.nodata = "NONE"

# 1 - raster manipulation
raster_manipulation(workspace, in_dem, in_culverts, maximum_distance, smooth_drop, sharp_drop, in_lake)
agree_dem = workspace + r"/AgreeDEM"
filled_channels = workspace + r"/Filled_channels"

# 2 - catchment processing
catchment_delineation(workspace, agree_dem, catchment_area)
catchments = workspace + r"\catchments"

# 3 - domain creation
domain_creation(workspace, in_dem, 5, catchments,
                in_buildings, in_landuse, inclination, output_folder)
arcpy.AddMessage('Success!')
