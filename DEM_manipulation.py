import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

# Input data
workspace = arcpy.GetParameterAsText(0)  # Output and scratch workspace
input_features = arcpy.GetParameterAsText(1)  # Culverts, ditches, rivers, etc. Polyline.
dem = arcpy.GetParameterAsText(2)  # Digital Elevation Model. Raster.
maximum_distance = int(arcpy.GetParameterAsText(3))  # Buffer around an input_feature. Length in cells. Integer.
smooth_drop = int(arcpy.GetParameterAsText(4))  # Smooth slope around an input_feature. Integer.
sharp_drop = int(arcpy.GetParameterAsText(5))  # sharp drop just below an input_feature. Integer.

# Output data
fillSinks = arcpy.GetParameterAsText(6)  # raster

# Local variables
agreeStrGeo = workspace + r"/agreeStrGeo"
vecEucDistGeo = workspace + r"/vecEucDistGeo"
bufferElevGeo = workspace + r"/bufferElevGeo"
vecEucAlloGeo = workspace + r"/vecEucAlloGeo"
bufEucAlloGeo = workspace + r"/bufEucAlloGeo"
bufEucDistGeo = workspace + r"/bufEucDistGeo"
smoothModGeo = workspace + r"/smoothModGeo"
sharpModGeo = workspace + r"/sharpModGeo"
agreeDEM = workspace + r"/agreeDEM"

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem
arcpy.env.nodata = "NONE"


# Processing
# DEM extent
left = arcpy.GetRasterProperties_management(dem, "LEFT")
bottom = arcpy.GetRasterProperties_management(dem, "BOTTOM")
right = arcpy.GetRasterProperties_management(dem, "RIGHT")
top = arcpy.GetRasterProperties_management(dem, "TOP")

# Polyline to raster
arcpy.PolylineToRaster_conversion(input_features, "OBJECTID", agreeStrGeo, "MAXIMUM_LENGTH", "NONE", dem)
arcpy.AddMessage('Polyline to raster. Done.')

# Con
agreeStrDEM = Con(agreeStrGeo, dem, "", "")
arcpy.AddMessage('AgreeStrDem. Done.')

# Minus
smoothGeo = Minus(agreeStrDEM, smooth_drop)
arcpy.AddMessage('SmoothGeo. Done.')

# Int
smoothGeoInt = Int(smoothGeo)
arcpy.AddMessage('SmoothGeoInt. Done.')

# New extent
arcpy.env.extent = arcpy.Extent(left, bottom, right, top)
arcpy.AddMessage('New extent. Done.')

# Euclidean Allocation
arcpy.gp.EucAllocation_sa(smoothGeoInt, vecEucAlloGeo, maximum_distance, "", dem, "VALUE",
                          vecEucDistGeo, "", "PLANAR", "", "")
arcpy.AddMessage('VecEucAlloGeo and vecEucDistGeo. Done.')

# Is Null
nullBuffGeo = IsNull(vecEucDistGeo)
arcpy.AddMessage('NullBuffGeo. Done.')

# Con #2
# bufferElevGeo = Con(nullBuffGeo, dem, "", "")  # does not work. Wrong number of bands in ArcMap
arcpy.gp.Con_sa(nullBuffGeo, dem, bufferElevGeo, "", "")
arcpy.AddMessage('BufferElevGeo. Done.')

# Int #2
bufferelevint = Int(bufferElevGeo)
arcpy.AddMessage('BufferElevInt. Done.')

# Euclidean Allocation #2
arcpy.gp.EucAllocation_sa(bufferelevint, bufEucAlloGeo, "", "", dem, "VALUE", bufEucDistGeo,
                          "", "PLANAR", "", "")
arcpy.AddMessage('Euclidean allocation. Done.')

# Minus #2
bufMinVecAllo = Minus(bufEucAlloGeo, vecEucAlloGeo)
arcpy.AddMessage('BufMinVecAllo. Done.')

# Plus
bufPlVecDist = Plus(bufEucDistGeo, vecEucDistGeo)
arcpy.AddMessage('BufPlVecDist. Done.')

# Divide
bufDivideGeo = Divide(bufMinVecAllo, bufPlVecDist)
arcpy.AddMessage('BufDivideGeo. Done.')

# Times
bufTimesGeo = Times(bufDivideGeo, vecEucDistGeo)
arcpy.AddMessage('BufTimesGeo. Done.')

# Plus #2
arcpy.gp.Plus_sa(vecEucAlloGeo, bufTimesGeo, smoothModGeo)
arcpy.AddMessage('SmoothModGeo. Done.')

# Minus #3
arcpy.gp.Minus_sa(smoothGeoInt, sharp_drop, sharpModGeo)
arcpy.AddMessage('SharpModGeo. Done.')

# Mosaic
arcpy.Mosaic_management("smoothModGeo;sharpModGeo", bufferElevGeo,
                        "LAST", "FIRST", "", "", "NONE")

# Con #3
arcpy.gp.Con_sa(dem, bufferElevGeo, agreeDEM, "", "")
arcpy.AddMessage('AgreeDEM. Done.')

# Fill
out_fillSinks = Fill(agreeDEM)
out_fillSinks.save(fillSinks)

# del temo rasters
arcpy.Delete_management(agreeStrGeo)
arcpy.Delete_management(vecEucDistGeo)
arcpy.Delete_management(bufferElevGeo)
arcpy.Delete_management(vecEucAlloGeo)
arcpy.Delete_management(bufEucAlloGeo)
arcpy.Delete_management(bufEucDistGeo)
arcpy.Delete_management(smoothModGeo)
arcpy.Delete_management(sharpModGeo)
arcpy.Delete_management(agreeDEM)
