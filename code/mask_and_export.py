import arcpy
from functions import mask_and_export
import os

mask = arcpy.GetParameterAsText(0)
in_rasters = arcpy.GetParameterAsText(1)
out_folder = arcpy.GetParameterAsText(2)

arcpy.AddMessage(in_rasters)
in_rasters_list = in_rasters.split(';')
arcpy.AddMessage(in_rasters_list)

mask_and_export(mask, in_rasters_list, out_folder)
