import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

# input data
workspace = arcpy.GetParameterAsText(0)
dem = arcpy.GetParameterAsText(1)
catchment_area = arcpy.GetParameterAsText(2)
if catchment_area == "#":
    catchment_area = 1

# output file
catchment = arcpy.GetParameterAsText(3)

# Local variables
tempBasin = workspace + r"/tempBasin"
streams = workspace + r"/streams"

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem
arcpy.env.nodata = "NONE"

# DEM cell size
cell_size_x_direction = arcpy.GetRasterProperties_management(dem, "CELLSIZEX")
cell_size_y_direction = arcpy.GetRasterProperties_management(dem, "CELLSIZEY")
cell_size_x_direction = float(cell_size_x_direction.getOutput(0))
cell_size_y_direction = float(cell_size_y_direction.getOutput(0))
arcpy.AddMessage(type(cell_size_x_direction))
arcpy.AddMessage(type(cell_size_y_direction))
cell_size = (cell_size_x_direction + cell_size_y_direction) / 2
if cell_size_x_direction != cell_size_y_direction:
    arcpy.AddMessage('Cell size in the x-direction is different from cell size in the y-direction!')

catchment_area = float(catchment_area)
catchment_area = (catchment_area * 1000000) / (cell_size_x_direction * cell_size_y_direction)
catchment_area = int(catchment_area)

# Script arguments
Expression = "VALUE > " + str(catchment_area)

# Flow direction
flowDir = FlowDirection(dem, "NORMAL", "")
arcpy.AddMessage('Flow direction raster has been built.')

# Flow accumulation
flowAcc = FlowAccumulation(flowDir, "", "INTEGER")
arcpy.AddMessage('Flow accumulation raster has been built.')

# Con
stream = Con(flowAcc, 1, "", Expression)
arcpy.AddMessage('Conditional raster has been built.')

# Stream link
strLn = StreamLink(stream, flowDir)
arcpy.AddMessage('Steam links has been found.')

# Stream to feature
StreamToFeature(strLn, flowDir, streams, "NO_SIMPLIFY")
arcpy.AddMessage('Steams has been converted to features.')

# Watershed
cat = Watershed(flowDir, strLn, "VALUE")
arcpy.AddMessage('The watershed raster has been built.')

# Build raster attribute table
arcpy.BuildRasterAttributeTable_management(cat, "Overwrite")

# Raster to polygon
arcpy.RasterToPolygon_conversion(cat, tempBasin, "NO_SIMPLIFY", "VALUE", "SINGLE_OUTER_PART", "")
arcpy.AddMessage('Raster to polygon. Done.')

# Dissolve
arcpy.Dissolve_management(tempBasin, catchment, "gridcode", "", "MULTI_PART", "DISSOLVE_LINES")
arcpy.AddMessage('Catchments areas have been created')

# Add field
arcpy.AddField_management(catchment, "GridID", "LONG", "", "", "", "GridID", "NULLABLE", "NON_REQUIRED", "")

# Calculate field
arcpy.CalculateField_management(catchment, "GridID", "!gridcode!", "PYTHON", "")

# Delete field
arcpy.DeleteField_management(catchment, "gridcode" "!")

# Add attribute index
arcpy.AddIndex_management(catchment, "GridID", "GridID_Index", "NON_UNIQUE", "ASCENDING")

# del temo layers
arcpy.Delete_management(tempBasin)

arcpy.AddMessage('The polygon conversion has been made. Success!')