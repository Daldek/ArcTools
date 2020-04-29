import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

# Input data
workspace = arcpy.GetParameterAsText(0)  # Output and scratch workspace
river_network = arcpy.GetParameterAsText(1)  # Culverts, ditches, rivers, etc. Polyline.
endorheic_water_bodies = arcpy.GetParameterAsText(2)
# Water bodies that are not connected to other surface waters. Polygon.
dem = arcpy.GetParameterAsText(3)  # Digital Elevation Model. Raster.
maximum_distance = int(arcpy.GetParameterAsText(4))  # Buffer around an river_network. Length in cells. Integer.
smooth_drop = int(arcpy.GetParameterAsText(5))  # Smooth slope around an river_network. Integer.
sharp_drop = int(arcpy.GetParameterAsText(6))  # sharp drop just below an river_network. Integer.

# Output data
fillSinks = arcpy.GetParameterAsText(7)  # output raster which will be saved in workspace specified before

# Local variables
lakes = workspace + r"/lakes"
agreeStrGeo = workspace + r"/agreeStrGeo"
vecEucDistGeo = workspace + r"/vecEucDistGeo"
bufferElevGeo = workspace + r"/bufferElevGeo"
vecEucAlloGeo = workspace + r"/vecEucAlloGeo"
bufEucAlloGeo = workspace + r"/bufEucAlloGeo"
bufEucDistGeo = workspace + r"/bufEucDistGeo"
smoothModGeo = workspace + r"/smoothModGeo"
sharpModGeo = workspace + r"/sharpModGeo"
agreeDEM = workspace + r"/agreeDEM"
field_name = "LakeElev"

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem
arcpy.env.nodata = "NONE"

# Processing
# Channel depth
if sharp_drop < smooth_drop:
    sharp_drop = smooth_drop
    arcpy.AddMessage('Sharp drop must be greater or equal smooth drop! Script will continue to run with equal values.')

# DEM cell size
cell_size_x_direction = arcpy.GetRasterProperties_management(dem, "CELLSIZEX")
cell_size_y_direction = arcpy.GetRasterProperties_management(dem, "CELLSIZEY")
cell_size_x_direction = float(cell_size_x_direction.getOutput(0))
cell_size_y_direction = float(cell_size_y_direction.getOutput(0))
cell_size = (cell_size_x_direction + cell_size_y_direction) / 2
if cell_size_x_direction != cell_size_y_direction:
    arcpy.AddMessage('Cell size in the x-direction is different from cell size in the y-direction!')

# Endorheic basins
if endorheic_water_bodies != "#":
    # New field
    arcpy.AddField_management(endorheic_water_bodies, field_name, "SHORT", "", "", "", "LakeElev", "NULLABLE",
                              "NON_REQUIRED", "")
    arcpy.AddMessage("New field has been created")

    # Assigning values to new filed
    arcpy.CalculateField_management(endorheic_water_bodies, field_name, 9999, "PYTHON_9.3")
    arcpy.AddMessage("Values have been assigned.")

    # Rasterization
    arcpy.PolygonToRaster_conversion(endorheic_water_bodies, field_name, lakes, "CELL_CENTER", "", dem)
    arcpy.AddMessage("Polygons have been rasterized.")

    # Mosaic to new raster
    arcpy.MosaicToNewRaster_management("lakes; dem", workspace, "dem_manip", "", "32_BIT_FLOAT", cell_size, 1,
                                       "FIRST", "FIRST")
    arcpy.AddMessage('New raster has been created')

    # Set null
    outSetNull = SetNull("dem_manip", "dem_manip", "Value = 9999")
    outSetNull.save("dem_lakes")
    arcpy.AddMessage('Null values have been assigned')

    dem = workspace + r"\dem_lakes"

# DEM extent
left = arcpy.GetRasterProperties_management(dem, "LEFT")
bottom = arcpy.GetRasterProperties_management(dem, "BOTTOM")
right = arcpy.GetRasterProperties_management(dem, "RIGHT")
top = arcpy.GetRasterProperties_management(dem, "TOP")

# Polyline to raster
arcpy.PolylineToRaster_conversion(river_network, "OBJECTID", agreeStrGeo, "MAXIMUM_LENGTH", "NONE", dem)
arcpy.AddMessage('Polylines have been rasterized')

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
arcpy.AddMessage('Mosaic. Done.')

# Con #3
arcpy.gp.Con_sa(dem, bufferElevGeo, agreeDEM, "", "")
arcpy.AddMessage('AgreeDEM. Done.')

# Fill
out_fillSinks = Fill(agreeDEM)
out_fillSinks.save(fillSinks)
arcpy.AddMessage('New raster has been created.')

# del temporary files
arcpy.AddMessage('Removing temporary files')
if endorheic_water_bodies != "#":
    arcpy.Delete_management("lakes")
    arcpy.Delete_management("dem_manip")
    arcpy.Delete_management("dem_lakes")

arcpy.Delete_management(agreeStrGeo)
arcpy.Delete_management(vecEucDistGeo)
arcpy.Delete_management(bufferElevGeo)
arcpy.Delete_management(vecEucAlloGeo)
arcpy.Delete_management(bufEucAlloGeo)
arcpy.Delete_management(bufEucDistGeo)
arcpy.Delete_management(smoothModGeo)
arcpy.Delete_management(sharpModGeo)
arcpy.Delete_management(agreeDEM)

arcpy.AddMessage('Temporary files have been removed. Now you can start the catchment processing')
