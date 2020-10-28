from functions import *

# variables
workspace = arcpy.GetParameterAsText(0)
group_number = int(arcpy.GetParameterAsText(1))
variable_value = arcpy.GetParameterAsText(2)

# environment
arcpy.env.workspace = workspace

# execute
ras_list = []
ras_names = arcpy.ListRasters()
for ras_name in ras_names:
    decoded_name = mike_tools_decoder(ras_name, group_number, variable_value)
    if decoded_name is not None:
        ras_list.append(decoded_name)

arcpy.AddMessage(ras_list)
