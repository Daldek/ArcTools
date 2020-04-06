import arcpy

# Input data
workspace = arcpy.GetParameterAsText(0)  # Output and scratch workspace
input_features = arcpy.GetParameterAsText(1)  # Culverts, ditches, rivers, etc. Polyline.
DEM = arcpy.GetParameterAsText(2)  # Digital Elevation Model. Raster.
maximum_distance = arcpy.GetParameterAsText(3)  # Buffer around an input_feature. Length in cells. Integer.
smooth_drop = arcpy.GetParameterAsText(4)  # Smooth slope around an input_feature. Integer.
sharp_drop = arcpy.GetParameterAsText(5)  # sharp drop just below an input_feature. Integer.

# Output data
output = arcpy.GetParameterAsText(6)  # raster

# Local variables
agreeStrGeo = "%Workspace%\\agreeStrGeo"
agreeStrDEM = "%Workspace%\\agreeStrDEM"
smoothGeo = "%Workspace%\\smoothGeo"
smoothGeoInt = "%Workspace%\\smoothGeoInt"
Output_direction_raster = ""
Output_back_direction_raster = ""
vecEucDistGeo = "%Workspace%\\vecEucDistGeo"
nullBuffGeo = "%Workspace%\\nullBuffGeo"
bufferElevGeo = "%Workspace%\\bufferElevGeo"
bufferelevint = "%Workspace%\\bufferelevint"
Output_direction_raster__2_ = ""
Output_back_direction_raster__2_ = ""
vecEucAlloGeo = "%Workspace%\\vecEucAlloGeo"
bufEucAlloGeo = "%Workspace%\\bufEucAlloGeo"
bufMinVecAllo = "%Workspace%\\bufMinVecAllo"
bufEucDistGeo = "%Workspace%\\bufEucDistGeo"
bufPlVecDist = "%Workspace%\\bufPlVecDist"
bufDivideGeo = "%Workspace%\\bufDivideGeo"
bufTimesGeo = "%Workspace%\\bufTimesGeo"
smoothModGeo = "%Workspace%\\smoothModGeo"
sharpModGeo = "%Workspace%\\sharpModGeo"
agreeDEM = "%Workspace%\\agreeDEM"
# Area_of_Interest = "in_memory\\{316D84AE-713C-4C1F-99C9-76E2CF862E14}"  # to trzeba przemyslec

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = DEM
arcpy.env.cellSize = DEM
arcpy.env.nodata = "NONE"


# Processing
# Polyline to raster
arcpy.PolylineToRaster_conversion(input_features, "OBJECTID", agreeStrGeo, "MAXIMUM_LENGTH", "NONE", DEM)

# Con
arcpy.gp.Con_sa(agreeStrGeo, DEM, agreeStrDEM, "", "")

# Minus
arcpy.gp.Minus_sa(agreeStrDEM, smooth_drop, smoothGeo)

# Int
arcpy.gp.Int_sa(smoothGeo, smoothGeoInt)

# Euclidean Allocation
arcpy.gp.EucAllocation_sa(smoothGeoInt, vecEucAlloGeo, maximum_distance, "", DEM, "VALUE",
                          vecEucDistGeo, Output_direction_raster, "PLANAR", "",
                          Output_back_direction_raster)

# Is Null
arcpy.gp.IsNull_sa(vecEucDistGeo, nullBuffGeo)

# Con #2
arcpy.gp.Con_sa(nullBuffGeo, DEM, bufferElevGeo, "", "")

# Int #2
arcpy.gp.Int_sa(bufferElevGeo, bufferelevint)

# Euclidean Allocation #2
arcpy.gp.EucAllocation_sa(bufferelevint, bufEucAlloGeo, "", "", DEM, "VALUE", bufEucDistGeo,
                          Output_direction_raster__2_, "PLANAR", "", Output_back_direction_raster__2_)

# Minus #2
arcpy.gp.Minus_sa(bufEucAlloGeo, vecEucAlloGeo, bufMinVecAllo)

# Plus
arcpy.gp.Plus_sa(bufEucDistGeo, vecEucDistGeo, bufPlVecDist)

# Divide
arcpy.gp.Divide_sa(bufMinVecAllo, bufPlVecDist, bufDivideGeo)

# Times
arcpy.gp.Times_sa(bufDivideGeo, vecEucDistGeo, bufTimesGeo)

# Plus #2
arcpy.gp.Plus_sa(vecEucAlloGeo, bufTimesGeo, smoothModGeo)

# Minus #3
arcpy.gp.Minus_sa(smoothGeoInt, sharp_drop, sharpModGeo)

# Mosaic
arcpy.Mosaic_management("smoothModGeo;sharpModGeo", bufferElevGeo,
                        "LAST", "FIRST", "", "", "NONE")

# Con #3
arcpy.gp.Con_sa(DEM, bufferElevGeo, agreeDEM, "", "")

# Calculate Statistics
# Nie wiem czy jest potrzebne
# arcpy.CalculateStatistics_management(agreeDEM, "1", "1", "", "OVERWRITE", Area_of_Interest)
# arcpy.CalculateStatistics_management(agreeDEM, "1", "1", "", "OVERWRITE")

# Fill
arcpy.gp.Fill_sa(agreeDEM, output, "")
