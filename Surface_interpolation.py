import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *

workspace = arcpy.GetParameterAsText(0)
inRaster = arcpy.GetParameterAsText(1)
outRaster = arcpy.GetParameterAsText(2)

# Env settings
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = inRaster
arcpy.env.cellSize = inRaster
arcpy.env.nodata = "NONE"

outCon = Con(IsNull(inRaster), FocalStatistics(inRaster, NbrRectangle(6, 6, "CELL"), "MEAN"), inRaster)

outCon.save(outRaster)
