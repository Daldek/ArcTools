from functions import *

workspace_gdb = arcpy.GetParameterAsText(0)
workspace_folder = arcpy.GetParameterAsText(1)
input_las_catalog = arcpy.GetParameterAsText(2)
coordinate_system = arcpy.GetParameterAsText(3)
class_codes = arcpy.GetParameterAsText(4)
cell_size = arcpy.GetParameterAsText(5)
output_raster = arcpy.GetParameterAsText(6)

las2dtm(workspace_gdb, workspace_folder, input_las_catalog,
        coordinate_system, class_codes, cell_size, output_raster)
arcpy.AddMessage('Success!')
