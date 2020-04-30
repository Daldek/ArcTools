import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

# input data
workspace = arcpy.GetParameterAsText(0)
dem = arcpy.GetParameterAsText(1)
catchment_area = arcpy.GetParameterAsText(2)
if catchment_area == "#":
    catchment_area = 0.25  # unit - square kilometers

# output file
catchment = arcpy.GetParameterAsText(3)

# Local variables
tempBasin = workspace + r"/tempBasin"
streams = workspace + r"/streams"
catchment_border = workspace + r"/catchment_border"
union_basins = workspace + r"/union_basins"

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
cell_size = (cell_size_x_direction + cell_size_y_direction) / 2
if cell_size_x_direction != cell_size_y_direction:
    arcpy.AddMessage('Cell size in the x-direction is different from cell size in the y-direction!')

# Square kilometers to number of cells
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
arcpy.AddMessage('Steam links have been found.')

# Stream to feature
StreamToFeature(strLn, flowDir, streams, "NO_SIMPLIFY")
arcpy.AddMessage('Streams have been converted to features.')

# Watershed
cat = Watershed(flowDir, strLn, "VALUE")
arcpy.AddMessage('The watershed raster has been built.')

# Build raster attribute table
arcpy.BuildRasterAttributeTable_management(cat, "Overwrite")

# Raster to polygon
arcpy.RasterToPolygon_conversion(cat, tempBasin, "NO_SIMPLIFY", "VALUE")
arcpy.AddMessage('Raster to polygon. Done.')

# Dissolve
arcpy.Dissolve_management(tempBasin, catchment, "gridcode", "", "MULTI_PART", "DISSOLVE_LINES")
arcpy.AddMessage('Catchments areas have been created')

# Add field
arcpy.AddField_management(catchment, "GridID", "LONG", "", "", "", "GridID", "NULLABLE", "NON_REQUIRED", "")

# Calculate field
arcpy.CalculateField_management(catchment, "GridID", "!gridcode!", "PYTHON", "")

# Delete field
arcpy.DeleteField_management(catchment, "gridcode")

# Add attribute index
arcpy.AddIndex_management(catchment, "GridID", "GridID_Index", "NON_UNIQUE", "ASCENDING")

# Polygon to line
arcpy.PolygonToLine_management(catchment, catchment_border, "IGNORE_NEIGHBORS")

# Feature to polygon
arcpy.FeatureToPolygon_management("catchment_border", tempBasin)

# Union
arcpy.Union_analysis([catchment, tempBasin], union_basins, "ALL", 0, "NO_GAPS")

# Dissolve
arcpy.Dissolve_management(union_basins, catchment, "GridID", "", "MULTI_PART", "DISSOLVE_LINES")
arcpy.AddMessage('Catchments areas have been created')

# Delete field
arcpy.DeleteField_management(catchment, "GridID")

# del temp layers
arcpy.Delete_management(tempBasin)
arcpy.Delete_management(catchment_border)
arcpy.Delete_management(union_basins)

arcpy.AddMessage('The polygon conversion has been made. Success!')
