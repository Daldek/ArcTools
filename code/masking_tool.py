from functions import *

# variables
workspace = arcpy.GetParameterAsText(0)
group_number = int(arcpy.GetParameterAsText(1))
variable_value = arcpy.GetParameterAsText(2)
cell_size = arcpy.GetParameterAsText(3)
threshold_value = arcpy.GetParameterAsText(4)
nodata_polygons = arcpy.GetParameterAsText(5)
domain = arcpy.GetParameterAsText(6)

# environment
arcpy.env.workspace = workspace
arcpy.env.scratchWorkspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.cellSize = cell_size
arcpy.env.nodata = "NONE"

# execute
masks_list = []
mask_paths_list = []
ras_names = arcpy.ListRasters()
for ras_name in ras_names:
    decoded_ras_name = mike_tools_decoder(ras_name, group_number, variable_value)
    if decoded_ras_name is not None:
        masks_list.append(decoded_ras_name)

for mask in masks_list:
    arcpy.AddMessage(mask)
    in_mask_path = workspace + "\\" + str(mask)
    arcpy.env.snapRaster = in_mask_path
    out_mask_path = workspace + "\\" + str(mask) + r"_mask"
    out_mask = mask_below_threshold(workspace, cell_size, in_mask_path, threshold_value, nodata_polygons, domain)
    out_mask.save(out_mask_path)
    for ras_name in ras_names:
        if mike_tools_decoder(out_mask_path, 2, '') == mike_tools_decoder(ras_name, 2, ''):
            ras_path = workspace + "\\" + str(ras_name)
            masked_raster_path = str(ras_path) + r"_masked"
            arcpy.AddMessage(out_mask_path + " will mask " + ras_path)
            arcpy.AddMessage("Output path " + masked_raster_path)
            masked_raster = ExtractByMask(ras_path, out_mask_path)
            masked_raster.save(masked_raster_path)

arcpy.RefreshCatalog(workspace)
