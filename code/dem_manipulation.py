from functions import *

# Input data
workspace = arcpy.GetParameterAsText(0)  # Output and scratch workspace
river_network = arcpy.GetParameterAsText(1)  # Culverts, ditches, rivers, etc. Polyline.
endorheic_water_bodies = arcpy.GetParameterAsText(2)
# Water bodies that are not connected to other surface waters. Polygon.
dem = arcpy.GetParameterAsText(3)  # Digital Elevation Model. Raster.
maximum_distance = int(arcpy.GetParameterAsText(4))  # Buffer around an river_network. Length in cells. Integer.
smooth_drop = int(arcpy.GetParameterAsText(5))  # Smooth slope around an river_network. Integer.
sharp_drop = int(arcpy.GetParameterAsText(6))  # sharp drop just below an river_network. Integer.

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem
arcpy.env.nodata = "NONE"

raster_manipulation(workspace, dem, river_network, maximum_distance, smooth_drop, sharp_drop, endorheic_water_bodies)
