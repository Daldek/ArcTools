import arcpy
from Functions import columns_rows_check

# Input
input_folder = arcpy.GetParameterAsText(0)

# Variables
model_domain_output_file = input_folder + str("/model_domain.asc")
land_use_output_file = input_folder + str("/land_use.asc")
roughness_output_file = input_folder + str("/roughness.asc")

columns_rows_check(land_use_output_file, model_domain_output_file, roughness_output_file)
arcpy.AddMessage('Success!')
