from functions import *

input_feature = arcpy.GetParameterAsText(0)

remove_unnecessary_fields(input_feature)
arcpy.AddMessage('Success!')
