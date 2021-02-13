from functions import *

workspace_gdb = arcpy.GetParameterAsText(0)  # geodatabase
workspace_folder = arcpy.GetParameterAsText(1)  # folder
input_las_catalog = arcpy.GetParameterAsText(2)  # folder where las files are saved
coordinate_system = arcpy.GetParameterAsText(3)  # output coordinate system, optional
class_codes = arcpy.GetParameterAsText(4)
cell_size = arcpy.GetParameterAsText(5)
output_raster_name = arcpy.GetParameterAsText(6)

las2dtm(workspace_gdb, workspace_folder, input_las_catalog,
        coordinate_system, class_codes, cell_size, output_raster_name)
arcpy.AddMessage('Success!')
